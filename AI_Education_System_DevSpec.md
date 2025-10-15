# AI 教学多智能体系统开发文档（Dev Spec）

## 一、产品功能概述

### 1.1 使用场景
- 教师上传**教学大纲** → 系统生成**统一教学计划**（Teacher Agent）
- Tutor Agent 根据统一计划**出题**、收集学生作答（含每题用时）、**自动批改**并给出**个体反馈报告**
- Classroom Agent 在统一计划基础上进行**个性化增量**（个体/小组）并输出**班级统计**与**学生个性化报告**
- 教师审核 Classroom 输出，**确认/微调**并发布最终课堂实施方案

### 1.2 主要功能
- 教学大纲管理：创建、查看、版本化  
- 统一教学计划（基线）生成与查看（Teacher Agent）  
- 题目生成、学生作答与计时、自动批改（Tutor Agent）  
- 学生个体报告、班级汇总报告（Classroom Agent）  
- 个性化教学方案（在基线计划上的增量）  
- 教师审核与发布（人类在环）  
- 学习报告可视化（前端 ECharts）

---

## 二、技术栈与规范

### 2.1 前端
- **框架**：Vue 3 + Vite  
- **路由**：Vue Router  
- **网络**：Axios（统一封装拦截器、错误处理）  
- **可视化**：ECharts  
- **代码规范**：ESLint（Airbnb Base）+ Prettier  
- **目录结构**：
  ```bash
  frontend/
  ├─ src/
  │  ├─ api/
  │  ├─ views/
  │  ├─ components/
  │  ├─ router/
  │  ├─ store/
  │  ├─ utils/
  │  └─ main.js
  ├─ vite.config.js
  └─ package.json
  ```

### 2.2 后端（Django / “dianjo”）
- **框架**：Django 4.x + Django REST Framework  
- **中间件**：corsheaders（开发阶段开放跨域）  
- **模型层**：Django ORM（SQLite 开发，PostgreSQL 生产）  
- **AI 接入**：OpenAI Python SDK（Teacher/Tutor/Classroom 封装于 `openai_utils.py`）  
- **目录结构**：
  ```bash
  backend/
  ├─ aiedu/
  ├─ core/
  │  ├─ models.py
  │  ├─ serializers.py
  │  ├─ views.py
  │  ├─ openai_utils.py
  │  ├─ services/
  │  └─ validators.py
  ├─ manage.py
  ├─ requirements.txt
  └─ .env
  ```

---

## 三、API 列表与说明

### 教学大纲（Teacher → System）
#### [POST] `/api/outline/`
创建教学大纲。
```json
{
  "title": "一次方程（七年级）",
  "content": "等式性质、移项、乘除互逆 ...",
  "duration_min": 35,
  "difficulty": "medium"
}
```

#### [GET] `/api/outline/{outline_id}/`
获取大纲及题目。

---

### Teacher Agent
#### [POST] `/api/teacher_agent/plan/{outline_id}/`
生成统一教学计划。
```json
{
  "outline_id": 12,
  "version": "v1.0",
  "objectives": ["..."],
  "sequence": ["等式平衡","移项与正负号","乘除互逆","综合练习"],
  "activities": [
    {"id":"A1","title":"引入示例","minutes":5},
    {"id":"A2","title":"讲解与板演","minutes":10}
  ]
}
```

---

### Tutor Agent
#### [POST] `/api/tutor/quiz/{outline_id}/`
生成题目。

#### [POST] `/api/submit_answer/`
学生作答。

#### [GET] `/api/feedback/{outline_id}/{student_id}/`
获取学生个体反馈。
```json
{
  "student_id": "S001",
  "outline_id": 12,
  "summary": {"total":8,"correct":6,"accuracy":0.75},
  "items": [{"qid":"Q1","correct":1,"time_sec":8.4}]
}
```

---

### Classroom Agent
#### [POST] `/api/classroom/aggregate/{outline_id}/`
聚合全班数据，生成班级报告 + 个性化方案。
```json
{
  "summary": {"accuracy_avg":0.68,"time_avg_sec":12.4},
  "plan_delta": {"group_overrides":[{"group":"low"}]},
  "students": [{"student_id":"S001"}]
}
```

#### [POST] `/api/classroom/publish/{outline_id}/`
教师确认发布最终方案。

---

## 四、数据库设计

### 主要表结构
| 表名 | 说明 |
|------|------|
| `teacher_outline` | 教学大纲 |
| `quiz_question` | 题库 |
| `student` | 学生信息 |
| `attempt` | 答题会话 |
| `attempt_answer` | 单题作答 |
| `unified_lesson_plan` | Teacher Agent 输出 |
| `personalization_delta` | Classroom Agent 输出 |

```sql
CREATE TABLE unified_lesson_plan (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  outline_id INTEGER,
  version VARCHAR(20),
  objectives TEXT,
  sequence TEXT,
  activities TEXT,
  checks TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 五、非功能性要求
- JWT 鉴权（生产）  
- 日志脱敏、INFO 级记录  
- 聚合性能 <3s（缓存）  
- LLM 调用失败自动重试 1 次  
- 单元测试覆盖率 >80%  

---

## 六、交付清单
- 前后端源码  
- 环境文件 `.env.example`  
- API 文档（本文件可导入 Postman）  
- 数据库迁移脚本  
- Demo 账号  
