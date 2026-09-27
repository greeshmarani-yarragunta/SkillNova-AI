import api from './api';

export const resumeService = {
  analyzeResume: async (formData) => {
    const response = await api.post('/resumes/analyze/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getHistory: async () => {
    const response = await api.get('/resumes/history/');
    return response.data;
  },

  getDetail: async (id) => {
    const response = await api.get(`/resumes/${id}/`);
    return response.data;
  },
};
