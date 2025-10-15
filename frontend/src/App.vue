<script setup>
import { ref, onMounted } from 'vue'
import * as api from './api/index.js'

const activeTab = ref('outline')
const outlines = ref([])
const selectedOutline = ref(null)
const loading = ref(false)
const message = ref('')

// 表单数据
const outlineForm = ref({
  title: '',
  content: '',
  duration_min: 45,
  difficulty: 'medium'
})

const studentForm = ref({
  student_id: '',
  name: '',
  grade: '',
  class_name: ''
})

// 加载大纲列表
const loadOutlines = async () => {
  try {
    loading.value = true
    outlines.value = await api.getOutlines()
  } catch (error) {
    message.value = '❌ 加载失败: ' + error.message
  } finally {
    loading.value = false
  }
}

// 创建教学大纲
const createOutline = async () => {
  try {
    loading.value = true
    await api.createOutline(outlineForm.value)
    message.value = '✅ 教学大纲创建成功!'
    outlineForm.value = { title: '', content: '', duration_min: 45, difficulty: 'medium' }
    await loadOutlines()
  } catch (error) {
    message.value = '❌ 创建失败: ' + error.message
  } finally {
    loading.value = false
  }
}

// 生成教学计划
const generatePlan = async (outlineId) => {
  try {
    loading.value = true
    const result = await api.generateLessonPlan(outlineId)
    message.value = `✅ 教学计划生成成功! (ID: ${result.plan_id})`
  } catch (error) {
    message.value = '❌ 生成失败: ' + error.message
  } finally {
    loading.value = false
  }
}

// 生成题目
const generateQuiz = async (outlineId) => {
  try {
    loading.value = true
    const result = await api.generateQuiz(outlineId, 5)
    message.value = `✅ 已生成 ${result.questions.length} 道题目!`
    console.log('题目:', result.questions)
  } catch (error) {
    message.value = '❌ 生成失败: ' + error.message
  } finally {
    loading.value = false
  }
}

// 创建学生
const createStudent = async () => {
  try {
    loading.value = true
    await api.createStudent(studentForm.value)
    message.value = `✅ 学生 ${studentForm.value.name} 创建成功!`
    studentForm.value = { student_id: '', name: '', grade: '', class_name: '' }
  } catch (error) {
    message.value = '❌ 创建失败: ' + error.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOutlines()
})
</script>

<template>
  <div class="container">
    <h1>🎓 AI 教学多智能体系统</h1>
    
    <!-- 提示消息 -->
    <div v-if="message" class="message" :class="message.includes('✅') ? 'success' : 'error'">
      {{ message }}
    </div>

    <!-- 标签页 -->
    <div class="tabs">
      <button @click="activeTab = 'outline'" :class="{ active: activeTab === 'outline' }">
        📝 教学大纲
      </button>
      <button @click="activeTab = 'agent'" :class="{ active: activeTab === 'agent' }">
        🤖 智能体操作
      </button>
      <button @click="activeTab = 'student'" :class="{ active: activeTab === 'student' }">
        👨‍🎓 学生管理
      </button>
    </div>

    <!-- 教学大纲标签页 -->
    <div v-if="activeTab === 'outline'" class="tab-content">
      <h2>创建教学大纲</h2>
      <form @submit.prevent="createOutline" class="form">
        <div class="form-group">
          <label>标题:</label>
          <input v-model="outlineForm.title" required placeholder="例: 一次方程(七年级)" />
        </div>
        <div class="form-group">
          <label>大纲内容:</label>
          <textarea v-model="outlineForm.content" rows="5" required 
                    placeholder="输入教学大纲内容..."></textarea>
        </div>
        <div class="form-group">
          <label>课时长度(分钟):</label>
          <input v-model.number="outlineForm.duration_min" type="number" required />
        </div>
        <div class="form-group">
          <label>难度:</label>
          <select v-model="outlineForm.difficulty">
            <option value="easy">简单</option>
            <option value="medium">中等</option>
            <option value="hard">困难</option>
          </select>
        </div>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '创建中...' : '创建大纲' }}
        </button>
      </form>

      <h2>现有大纲列表</h2>
      <div v-if="outlines.length === 0" class="empty">
        暂无大纲,请先创建一个教学大纲
      </div>
      <div v-else class="outline-list">
        <div v-for="outline in outlines" :key="outline.id" class="outline-card">
          <h3>{{ outline.title }}</h3>
          <p><strong>难度:</strong> {{ outline.difficulty }} | <strong>时长:</strong> {{ outline.duration_min }}分钟</p>
          <p class="content">{{ outline.content.substring(0, 100) }}...</p>
          <p class="time">创建时间: {{ new Date(outline.created_at).toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <!-- 智能体操作标签页 -->
    <div v-if="activeTab === 'agent'" class="tab-content">
      <h2>智能体操作</h2>
      <p>选择一个大纲进行智能体操作:</p>
      
      <div v-if="outlines.length === 0" class="empty">
        请先创建教学大纲
      </div>
      <div v-else class="outline-list">
        <div v-for="outline in outlines" :key="outline.id" class="outline-card">
          <h3>{{ outline.title }}</h3>
          <div class="actions">
            <button @click="generatePlan(outline.id)" :disabled="loading" class="btn-secondary">
              📋 生成教学计划 (Teacher Agent)
            </button>
            <button @click="generateQuiz(outline.id)" :disabled="loading" class="btn-secondary">
              📝 生成题目 (Tutor Agent)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 学生管理标签页 -->
    <div v-if="activeTab === 'student'" class="tab-content">
      <h2>创建学生</h2>
      <form @submit.prevent="createStudent" class="form">
        <div class="form-group">
          <label>学号:</label>
          <input v-model="studentForm.student_id" required placeholder="例: S001" />
        </div>
        <div class="form-group">
          <label>姓名:</label>
          <input v-model="studentForm.name" required placeholder="例: 张三" />
        </div>
        <div class="form-group">
          <label>年级:</label>
          <input v-model="studentForm.grade" placeholder="例: 七年级" />
        </div>
        <div class="form-group">
          <label>班级:</label>
          <input v-model="studentForm.class_name" placeholder="例: 1班" />
        </div>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '创建中...' : '创建学生' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

.message {
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 5px;
  font-weight: bold;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #ddd;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.tabs button:hover {
  background-color: #f0f0f0;
}

.tabs button.active {
  border-bottom: 3px solid #42b883;
  color: #42b883;
  font-weight: bold;
}

.tab-content {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.form {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #359268;
}

.btn-secondary {
  background-color: #3498db;
  color: white;
  margin-right: 10px;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
  font-style: italic;
}

.outline-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.outline-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.outline-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.outline-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.outline-card .content {
  color: #666;
  line-height: 1.5;
}

.outline-card .time {
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

.actions {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.actions button {
  flex: 1;
  min-width: 150px;
}
</style>
