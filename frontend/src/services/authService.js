import api from './api';

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/profile/', profileData);
    return response.data;
  },

  getSkills: async () => {
    const response = await api.get('/skills/');
    return response.data;
  },

  createSkill: async (skillData) => {
    const response = await api.post('/skills/', skillData);
    return response.data;
  },

  deleteSkill: async (id) => {
    const response = await api.delete(`/skills/${id}/`);
    return response.data;
  },

  getStudentSkills: async () => {
    const response = await api.get('/student/skills/');
    return response.data;
  },

  addStudentSkill: async (skillId, proficiencyLevel = 'Beginner') => {
    const response = await api.post('/student/skills/', {
      skill_id: skillId,
      proficiency_level: proficiencyLevel,
    });
    return response.data;
  },

  removeStudentSkill: async (studentSkillId) => {
    const response = await api.delete(`/student/skills/${studentSkillId}/`);
    return response.data;
  },

  getAdminStats: async () => {
    const response = await api.get('/admin/stats/');
    return response.data;
  },

  getAdminUsers: async (role = '', search = '') => {
    let url = '/admin/users/?';
    if (role) url += `role=${role}&`;
    if (search) url += `search=${encodeURIComponent(search)}`;
    const response = await api.get(url);
    return response.data;
  },

  updateAdminUser: async (userId, data) => {
    const response = await api.patch(`/admin/users/${userId}/`, data);
    return response.data;
  },

  createAdminInstructor: async (instructorData) => {
    const response = await api.post('/admin/instructors/', instructorData);
    return response.data;
  },
};
