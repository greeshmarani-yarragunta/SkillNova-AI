import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import { authService } from '../../services/authService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiHelpCircle, FiZap, FiCheck, FiEdit2, FiTrash2,
  FiCheckCircle, FiAlertCircle, FiArrowRight, FiList
} from 'react-icons/fi';

const AIQuestionGeneratorPage = () => {
  const [skills, setSkills] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [selectedSkillId, setSelectedSkillId] = useState('');
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [questionCount, setQuestionCount] = useState(5);
  const [topic, setTopic] = useState('General');
  const [generating, setGenerating] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [error, setError] = useState('');

  // Editing state
  const [editingDraftId, setEditingDraftId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const loadData = async () => {
    try {
      const [skillsData, draftsData] = await Promise.all([
        authService.getSkills(),
        aiService.getInstructorQuestions({ status: 'draft' }),
      ]);
      setSkills(skillsData || []);
      setDrafts(draftsData || []);
      if (skillsData.length > 0 && !selectedSkillId) {
        setSelectedSkillId(skillsData[0].id);
      }
    } catch (err) {
      console.error('Failed to load generator resources', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedSkillId) {
      setError('Please select a skill.');
      return;
    }
    setError('');
    setSuccessMessage('');
    setGenerating(true);

    try {
      const newQuestions = await aiService.instructorGenerateQuestions(
        selectedSkillId,
        difficulty,
        questionCount,
        topic
      );
      setSuccessMessage(`Successfully generated ${newQuestions.length} draft questions! Review and approve them below.`);
      await loadData();
    } catch (err) {
      setError('Failed to generate AI questions. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const startEdit = (draft) => {
    setEditingDraftId(draft.id);
    setEditForm({
      question_text: draft.question_text,
      option_a: draft.option_a,
      option_b: draft.option_b,
      option_c: draft.option_c,
      option_d: draft.option_d,
      correct_option: draft.correct_option,
      explanation: draft.explanation,
      topic: draft.topic,
      difficulty: draft.difficulty,
    });
  };

  const handleSaveEdit = async (draftId) => {
    try {
      await aiService.updateInstructorQuestion(draftId, editForm);
      setEditingDraftId(null);
      await loadData();
    } catch (err) {
      console.error('Failed to save draft edits', err);
      alert('Failed to save changes.');
    }
  };

  const handleApprove = async (draftId) => {
    try {
      await aiService.approveInstructorQuestion(draftId);
      setDrafts((prev) => prev.filter((d) => d.id !== draftId));
      setSuccessMessage('Question approved and added to active assessment pool!');
    } catch (err) {
      console.error('Failed to approve question', err);
      alert('Failed to approve question.');
    }
  };

  const handleDelete = async (draftId) => {
    if (!window.confirm('Delete this draft question?')) return;
    try {
      await aiService.deleteInstructorQuestion(draftId);
      setDrafts((prev) => prev.filter((d) => d.id !== draftId));
    } catch (err) {
      console.error('Failed to delete draft', err);
    }
  };

  if (loading) return <LoadingSpinner message="Preparing AI question generator..." />;

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text)', marginBottom: '0.25rem' }}>
            AI Question Generator
          </h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
            Generate high-quality multiple choice assessment questions using Google Gemini and expert heuristics.
          </p>
        </div>

        <Link to="/instructor/questions" className="btn btn-secondary">
          <FiList /> View Question Bank
        </Link>
      </div>

      {successMessage && (
        <div style={{ padding: '0.85rem 1.25rem', background: 'var(--success-bg)', border: '1px solid var(--success-border)', borderRadius: 'var(--radius-md)', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
          <FiCheckCircle /> {successMessage}
        </div>
      )}

      {error && (
        <div style={{ padding: '0.85rem 1.25rem', background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', borderRadius: 'var(--radius-md)', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
          <FiAlertCircle /> {error}
        </div>
      )}

      {/* Generator Form Card */}
      <div className="card">
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text)', marginBottom: '1.25rem' }}>
          Configure AI Generation Set
        </h2>

        <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="grid grid-cols-4 gap-4">
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Target Skill</label>
              <select
                className="form-select"
                value={selectedSkillId}
                onChange={(e) => setSelectedSkillId(e.target.value)}
                required
              >
                {skills.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Subtopic Focus</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Memory, OOP, Async"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Difficulty</label>
              <select
                className="form-select"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Question Count</label>
              <select
                className="form-select"
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
              >
                <option value={3}>3 Questions</option>
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="submit"
              disabled={generating}
              className="btn btn-primary"
              style={{ minWidth: '220px' }}
            >
              {generating ? (
                <>
                  <span className="animate-spin">⏳</span> Generating with AI...
                </>
              ) : (
                <>
                  <FiZap /> Generate Questions
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Drafts Review Section */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text)' }}>
              Pending Review Drafts ({drafts.length})
            </h2>
            <p style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
              Questions generated by AI remain in draft until you review, edit, and approve them.
            </p>
          </div>
        </div>

        {drafts.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--muted)' }}>
            <FiCheckCircle style={{ fontSize: '2rem', marginBottom: '0.5rem', color: 'var(--success)' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)' }}>
              All Caught Up!
            </h3>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              No pending drafts awaiting review. Generate a new set above to create more questions.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {drafts.map((draft, idx) => {
              const isEditing = editingDraftId === draft.id;

              return (
                <div key={draft.id} className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {isEditing ? (
                    /* Inline Editing Mode */
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Question Text</label>
                        <textarea
                          className="form-textarea"
                          rows="2"
                          value={editForm.question_text}
                          onChange={(e) => setEditForm({ ...editForm, question_text: e.target.value })}
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        {['a', 'b', 'c', 'd'].map((k) => (
                          <div key={k} className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Option {k.toUpperCase()}</label>
                            <input
                              type="text"
                              className="form-input"
                              value={editForm[`option_${k}`]}
                              onChange={(e) => setEditForm({ ...editForm, [`option_${k}`]: e.target.value })}
                            />
                          </div>
                        ))}
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Correct Option</label>
                          <select
                            className="form-select"
                            value={editForm.correct_option}
                            onChange={(e) => setEditForm({ ...editForm, correct_option: e.target.value })}
                          >
                            <option value="A">Option A</option>
                            <option value="B">Option B</option>
                            <option value="C">Option C</option>
                            <option value="D">Option D</option>
                          </select>
                        </div>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Topic</label>
                          <input
                            type="text"
                            className="form-input"
                            value={editForm.topic}
                            onChange={(e) => setEditForm({ ...editForm, topic: e.target.value })}
                          />
                        </div>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Difficulty</label>
                          <select
                            className="form-select"
                            value={editForm.difficulty}
                            onChange={(e) => setEditForm({ ...editForm, difficulty: e.target.value })}
                          >
                            <option value="Beginner">Beginner</option>
                            <option value="Intermediate">Intermediate</option>
                            <option value="Advanced">Advanced</option>
                          </select>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Explanation</label>
                        <textarea
                          className="form-textarea"
                          rows="2"
                          value={editForm.explanation}
                          onChange={(e) => setEditForm({ ...editForm, explanation: e.target.value })}
                        />
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <button onClick={() => setEditingDraftId(null)} className="btn btn-secondary btn-sm">
                          Cancel
                        </button>
                        <button onClick={() => handleSaveEdit(draft.id)} className="btn btn-primary btn-sm">
                          Save Changes
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Display Mode */
                    <>
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                            <span className="badge badge-primary">{draft.skill_name}</span>
                            <span className="badge badge-neutral">{draft.difficulty}</span>
                            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Topic: {draft.topic}</span>
                          </div>
                          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text)', lineHeight: 1.4 }}>
                            {draft.question_text}
                          </h3>
                        </div>

                        <span className="badge badge-warning" style={{ fontSize: '0.75rem', flexShrink: 0 }}>
                          ⏳ Needs Approval
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-3" style={{ fontSize: '0.875rem' }}>
                        {[
                          { key: 'A', text: draft.option_a },
                          { key: 'B', text: draft.option_b },
                          { key: 'C', text: draft.option_c },
                          { key: 'D', text: draft.option_d },
                        ].map((opt) => (
                          <div
                            key={opt.key}
                            style={{
                              padding: '0.65rem 0.85rem',
                              borderRadius: 'var(--radius-sm)',
                              background: opt.key === draft.correct_option ? 'var(--success-bg)' : 'var(--background-secondary)',
                              border: opt.key === draft.correct_option ? '1px solid var(--success-border)' : '1px solid var(--border)',
                              color: opt.key === draft.correct_option ? 'var(--success)' : 'var(--text-secondary)',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                            }}
                          >
                            <strong>{opt.key}:</strong> {opt.text}
                            {opt.key === draft.correct_option && <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>(Correct)</span>}
                          </div>
                        ))}
                      </div>

                      {draft.explanation && (
                        <div style={{ fontSize: '0.825rem', color: 'var(--muted)', background: 'var(--background-secondary)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)' }}>
                          <strong>Explanation:</strong> {draft.explanation}
                        </div>
                      )}

                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
                        <button
                          onClick={() => startEdit(draft)}
                          className="btn btn-secondary btn-sm"
                        >
                          <FiEdit2 /> Edit
                        </button>
                        <button
                          onClick={() => handleDelete(draft.id)}
                          className="btn btn-outline btn-sm"
                          style={{ color: 'var(--danger)' }}
                        >
                          <FiTrash2 /> Discard
                        </button>
                        <button
                          onClick={() => handleApprove(draft.id)}
                          className="btn btn-primary btn-sm"
                        >
                          <FiCheck /> Approve & Add to Pool
                        </button>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIQuestionGeneratorPage;
