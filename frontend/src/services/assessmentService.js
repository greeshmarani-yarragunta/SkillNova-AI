import api from './api';

export const assessmentService = {
  generateAssessment: async (skillId, difficulty = 'Intermediate', questionCount = 30) => {
    const response = await api.post('/assessments/generate/', {
      skill_id: skillId,
      difficulty,
      question_count: 30,
    });
    return response.data;
  },

  submitAssessment: async (assessmentId, answers) => {
    const response = await api.post(`/assessments/${assessmentId}/submit/`, { answers });
    return response.data;
  },

  getAssessmentResults: async () => {
    const response = await api.get('/assessments/results/');
    return response.data;
  },

  getAssessmentDetail: async (assessmentId) => {
    const response = await api.get(`/assessments/${assessmentId}/`);
    return response.data;
  },


  getAdminAssessments: async (params = {}) => {
    const response = await api.get('/admin/assessments/', { params });
    return response.data;
  },
};
