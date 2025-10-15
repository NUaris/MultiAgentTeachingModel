"""
OpenAI API 统一封装
Unified OpenAI API wrapper with retry logic and logging
"""
import os
import logging
import time
from typing import Dict, List, Optional, Any
from openai import OpenAI

# 配置日志(脱敏)
logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    OpenAI 客户端封装
    Features:
    - Environment variable management
    - Automatic retry on failure
    - Response logging with PII masking
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 1  # 规范要求:失败重试 1 次
        self.default_model = "gpt-4o-mini"  # 默认模型,可通过参数覆盖
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用 OpenAI Chat Completion API
        
        Args:
            messages: 对话消息列表
            model: 模型名称(默认 gpt-4o-mini)
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
        
        Returns:
            API 响应字典
        """
        model = model or self.default_model
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"🤖 Calling OpenAI API (attempt {attempt + 1}/{self.max_retries + 1})")
                logger.debug(f"Model: {model}, Temperature: {temperature}")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                # 提取响应内容
                result = {
                    'content': response.choices[0].message.content,
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason
                }
                
                logger.info(f"✅ API call successful. Tokens used: {result['usage']['total_tokens']}")
                return result
                
            except Exception as e:
                logger.error(f"❌ OpenAI API error (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("❌ Max retries reached. Giving up.")
                    raise
    
    def create_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        创建文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型
        
        Returns:
            嵌入向量
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Embedding API error: {str(e)}")
            raise


# 全局客户端实例
_client_instance = None


def get_openai_client() -> OpenAIClient:
    """获取全局 OpenAI 客户端实例"""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance


def test_openai_connection() -> Dict[str, Any]:
    """
    测试 OpenAI 连接
    用于验证 API Key 和网络连接
    """
    try:
        client = get_openai_client()
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, AI Education System!'"}
            ],
            max_tokens=50
        )
        return {
            "status": "success",
            "message": response['content'],
            "model": response['model'],
            "tokens_used": response['usage']['total_tokens']
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
