import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiList, FiPlus, FiEdit, FiTrash2, FiCheckCircle,
  FiSearch, FiFilter, FiCheck, FiX, FiHelpCircle, FiAward
} from 'react-icons/fi';

const InstructorQuestionsPage = () => {
  const [searchParams] = useSearchParams();
  const [questions, setQuestions] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  // Modal State for Manual Creation / Editing
  const [modalOpen, setModalOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [formData, setFormData] = useState({
    skill_id: '',
    topic: 'General',
    difficulty: 'Intermediate',
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_option: 'A',
    explanation: '',
    is_published: true,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (searchParams.get('new') === 'true') {
      setEditingQuestion(null);
      setModalOpen(true);
    }
  }, [searchParams]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [qData, sData] = await Promise.all([
        aiService.getInstructorQuestions(),
        authService.getSkills(),
      ]);
      setQuestions(qData || []);
      setSkills(sData || []);
      if (sData.length > 0 && !formData.skill_id) {
        setFormData((prev) => ({ ...prev, skill_id: sData[0].id }));
      }
    } catch (err) {
      console.error('Failed to load instructor questions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreateModal = () => {
    setEditingQuestion(null);
    setFormData({
      skill_id: skills.length > 0 ? skills[0].id : '',
      topic: 'General',
      difficulty: 'Intermediate',
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_option: 'A',
      explanation: '',
      is_published: true,
    });
    setModalOpen(true);
  };

  const handleOpenEditModal = (q) => {
    setEditingQuestion(q);
    setFormData({
      skill_id: q.skill,
      topic: q.topic || 'General',
      difficulty: q.difficulty || 'Intermediate',
      question_text: q.question_text || '',
      option_a: q.option_a || '',
      option_b: q.option_b || '',
      option_c: q.option_c || '',
      option_d: q.option_d || '',
      correct_option: q.correct_option || 'A',
      explanation: q.explanation || '',
      is_published: q.is_published,
    });
    setModalOpen(true);
  };

  const handleSaveQuestion = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      if (editingQuestion) {
        const updated = await aiService.updateInstructorQuestion(editingQuestion.id, formData);
        setQuestions((prev) => prev.map((q) => (q.id === editingQuestion.id ? updated : q)));
        setMessage('Question updated successfully.');
      } else {
        const created = await aiService.createInstructorQuestion(formData);
        setQuestions((prev) => [created, ...prev]);
        setMessage('Question added to assessment bank.');
      }
      setModalOpen(false);
    } catch (err) {
      console.error('Save question failed', err);
      alert(err.response?.data?.error || 'Failed to save question.');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      const res = await aiService.approveInstructorQuestion(id);
      setQuestions((prev) =>
        prev.map((q) => (q.id === id ? { ...q, is_reviewed: true, is_published: true } : q))
      );
      alert('Question approved and added to active assessment pool!');
    } catch (err) {
      console.error('Approve failed', err);
      alert('Failed to approve question.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this question?')) return;
    try {
      await aiService.deleteInstructorQuestion(id);
      setQuestions((prev) => prev.filter((q) => q.id !== id));
    } catch (err) {
      console.error('Delete failed', err);
      alert('Failed to delete question.');
    }
  };

  // Client-side filtering
  const filteredQuestions = questions.filter((q) => {
    const matchesSkill = !selectedSkill || String(q.skill) === String(selectedSkill);
    const matchesDifficulty = !selectedDifficulty || q.difficulty?.toLowerCase() === selectedDifficulty.toLowerCase();
    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'approved' && q.is_published) ||
      (statusFilter === 'draft' && !q.is_published);
    const matchesSearch =
      !search ||
      q.question_text?.toLowerCase().includes(search.toLowerCase()) ||
      q.topic?.toLowerCase().includes(search.toLowerCase());

    return matchesSkill && matchesDifficulty && matchesStatus && matchesSearch;
  });

  if (loading) return <LoadingSpinner message="Loading question bank..." />;

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.25rem' }}>
            Question Bank Management
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
            Create, moderate, edit, and approve questions for student AI skill assessments.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/instructor/ai-questions" className="btn btn-secondary">
            <FiHelpCircle /> Generate AI Questions
          </Link>
          <button onClick={handleOpenCreateModal} className="btn btn-primary">
            <FiPlus /> Create Question Manually
          </button>
        </div>
      </div>

      {message && (
        <div style={{ padding: '0.75rem 1rem', background: 'var(--success-bg)', border: '1px solid var(--success-border)', borderRadius: 'var(--radius-md)', color: 'var(--success)', fontSize: '0.9rem' }}>
          ✓ {message}
        </div>
      )}

      {/* Filter Toolbar */}
      <div
        className="card"
        style={{
          padding: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flex: 1, minWidth: '220px' }}>
          <FiSearch style={{ color: 'var(--muted)' }} />
          <input
            type="text"
            className="form-input"
            style={{ padding: '0.5rem 0.75rem', border: 'none', background: 'transparent' }}
            placeholder="Search questions by text or topic..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          {/* Status Filter */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses ({questions.length})</option>
            <option value="approved">Approved & Active</option>
            <option value="draft">Review Pending / Drafts</option>
          </select>

          {/* Skill Filter */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedSkill}
            onChange={(e) => setSelectedSkill(e.target.value)}
          >
            <option value="">All Skills</option>
            {skills.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            <option value="">All Difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {/* Questions Table */}
      {filteredQuestions.length === 0 ? (
        <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--muted)' }}>
          <FiList style={{ fontSize: '2rem', marginBottom: '0.5rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>No Questions Found</h3>
          <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
            No questions match your current filters. Create one manually or generate a set using AI!
          </p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '40%' }}>Question</th>
                <th>Skill</th>
                <th>Topic</th>
                <th>Difficulty</th>
                <th>Answer</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredQuestions.map((q) => (
                <tr key={q.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text)', lineHeight: 1.4, marginBottom: '0.25rem' }}>
                      {q.question_text}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
                      A: {q.option_a?.slice(0, 30)}... | B: {q.option_b?.slice(0, 30)}...
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                      {q.skill_name || 'Skill'}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{q.topic}</span>
                  </td>
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                      {q.difficulty}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 800, color: 'var(--primary)' }}>Option {q.correct_option}</span>
                  </td>
                  <td>
                    {q.is_published ? (
                      <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                        ✓ Approved
                      </span>
                    ) : (
                      <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>
                        ⏳ Draft
                      </span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      {!q.is_published && (
                        <button
                          onClick={() => handleApprove(q.id)}
                          className="btn btn-outline btn-sm"
                          style={{ padding: '0.35rem 0.6rem', color: 'var(--success)', borderColor: 'var(--success)' }}
                          title="Approve & Publish into Test Pool"
                        >
                          <FiCheck /> Approve
                        </button>
                      )}
                      <button
                        onClick={() => handleOpenEditModal(q)}
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.35rem 0.6rem' }}
                        title="Edit Question"
                      >
                        <FiEdit />
                      </button>
                      <button
                        onClick={() => handleDelete(q.id)}
                        className="btn btn-outline btn-sm"
                        style={{ padding: '0.35rem 0.6rem', color: 'var(--danger)' }}
                        title="Delete Question"
                      >
                        <FiTrash2 />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create / Edit Question Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div
            className="modal-content fade-in"
            onClick={(e) => e.stopPropagation()}
            style={{ maxWidth: '650px', padding: '1.75rem' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text)' }}>
                {editingQuestion ? 'Edit Question' : 'Create New Assessment Question'}
              </h2>
              <button onClick={() => setModalOpen(false)} className="btn btn-secondary btn-sm" style={{ padding: '0.35rem' }}>
                <FiX />
              </button>
            </div>

            <form onSubmit={handleSaveQuestion} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="grid grid-cols-3 gap-3">
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Skill</label>
                  <select
                    className="form-select"
                    value={formData.skill_id}
                    onChange={(e) => setFormData({ ...formData, skill_id: e.target.value })}
                    required
                  >
                    {skills.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Topic</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.topic}
                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                    placeholder="e.g. OOP, Memory, Async"
                    required
                  />
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Difficulty</label>
                  <select
                    className="form-select"
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Question Text</label>
                <textarea
                  className="form-textarea"
                  rows="3"
                  value={formData.question_text}
                  onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                  placeholder="Enter the full technical question..."
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Option A</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.option_a}
                    onChange={(e) => setFormData({ ...formData, option_a: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Option B</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.option_b}
                    onChange={(e) => setFormData({ ...formData, option_b: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Option C</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.option_c}
                    onChange={(e) => setFormData({ ...formData, option_c: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Option D</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.option_d}
                    onChange={(e) => setFormData({ ...formData, option_d: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Correct Option</label>
                  <select
                    className="form-select"
                    value={formData.correct_option}
                    onChange={(e) => setFormData({ ...formData, correct_option: e.target.value })}
                  >
                    <option value="A">Option A</option>
                    <option value="B">Option B</option>
                    <option value="C">Option C</option>
                    <option value="D">Option D</option>
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Publication Status</label>
                  <select
                    className="form-select"
                    value={formData.is_published ? 'true' : 'false'}
                    onChange={(e) => setFormData({ ...formData, is_published: e.target.value === 'true' })}
                  >
                    <option value="true">Approved & Active</option>
                    <option value="false">Save as Draft</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Explanation</label>
                <textarea
                  className="form-textarea"
                  rows="2"
                  value={formData.explanation}
                  onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
                  placeholder="Explain why this answer is correct..."
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.75rem' }}>
                <button type="button" onClick={() => setModalOpen(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={saving} className="btn btn-primary">
                  {saving ? 'Saving...' : editingQuestion ? 'Update Question' : 'Add to Bank'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InstructorQuestionsPage;
