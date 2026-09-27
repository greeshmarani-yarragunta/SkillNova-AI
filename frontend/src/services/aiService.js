import api from './api';

export const aiService = {
  askAssistant: async (question) => {
    const response = await api.post('/ai/ask/', { question });
    return response.data;
  },

  getChatHistory: async () => {
    const response = await api.get('/ai/chat-history/');
    return response.data;
  },

  generateInterview: async (targetRole, experienceLevel, skills) => {
    const response = await api.post('/ai/interview/generate/', {
      target_role: targetRole,
      experience_level: experienceLevel,
      skills,
    });
    return response.data;
  },

  submitInterviewAnswers: async (sessionId, answers) => {
    const response = await api.post(`/ai/interview/${sessionId}/submit/`, { answers });
    return response.data;
  },

  getInterviewHistory: async () => {
    const response = await api.get('/ai/interview/history/');
    return response.data;
  },

  getInterviewDetail: async (sessionId) => {
    const response = await api.get(`/ai/interview/${sessionId}/`);
    return response.data;
  },

  // Instructor Question Management
  instructorGenerateQuestions: async (skillId, difficulty, questionCount, topic = 'General') => {
    const response = await api.post('/ai/instructor-questions/generate/', {
      skill_id: skillId,
      difficulty,
      question_count: questionCount,
      topic,
    });
    return response.data;
  },

  getInstructorQuestions: async (params = {}) => {
    const response = await api.get('/ai/instructor-questions/', { params });
    return response.data;
  },

  createInstructorQuestion: async (questionData) => {
    const response = await api.post('/ai/instructor-questions/', questionData);
    return response.data;
  },

  updateInstructorQuestion: async (id, questionData) => {
    const response = await api.patch(`/ai/instructor-questions/${id}/`, questionData);
    return response.data;
  },

  approveInstructorQuestion: async (id) => {
    const response = await api.post(`/ai/instructor-questions/${id}/approve/`);
    return response.data;
  },

  deleteInstructorQuestion: async (id) => {
    const response = await api.delete(`/ai/instructor-questions/${id}/`);
    return response.data;
  },

  getInstructorStats: async () => {
    const response = await api.get('/instructor/stats/');
    return response.data;
  },

  getInstructorPerformance: async (params = {}) => {
    const response = await api.get('/instructor/performance/', { params });
    return response.data;
  },
};
