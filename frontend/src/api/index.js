import http from './http'

// 教学大纲相关
export const createOutline = (data) => http.post('/outline/', data)
export const getOutlines = () => http.get('/outlines/')
export const getOutline = (id) => http.get(`/outline/${id}/`)

// Teacher Agent
export const generateLessonPlan = (outlineId) => http.post(`/teacher_agent/plan/${outlineId}/`)

// Tutor Agent
export const generateQuiz = (outlineId, numQuestions = 5) => 
  http.post(`/tutor/quiz/${outlineId}/`, { num_questions: numQuestions })

export const submitAnswer = (data) => http.post('/submit_answer/', data)
export const getFeedback = (outlineId, studentId) => 
  http.get(`/feedback/${outlineId}/${studentId}/`)

// Classroom Agent
export const aggregateClassData = (outlineId) => 
  http.post(`/classroom/aggregate/${outlineId}/`)
export const publishPlan = (outlineId, personalizationId) => 
  http.post(`/classroom/publish/${outlineId}/`, { personalization_id: personalizationId })

// 学生相关
export const createStudent = (data) => http.post('/student/', data)
export const createAttempt = (studentId, outlineId) => 
  http.post('/attempt/', { student_id: studentId, outline_id: outlineId })
