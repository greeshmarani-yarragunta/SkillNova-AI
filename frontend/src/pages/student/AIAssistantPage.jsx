import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import LoadingSpinner from '../../components/LoadingSpinner';
import {
  FiSend, FiCpu, FiUser, FiCode, FiCheckCircle,
  FiHelpCircle, FiCopy, FiCheck, FiCornerDownLeft
} from 'react-icons/fi';

const AIAssistantPage = () => {
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [userSelectedPractice, setUserSelectedPractice] = useState({});

  const chatEndRef = useRef(null);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await aiService.getChatHistory();
        if (history && history.length > 0) {
          setMessages(history);
        } else {
          // Welcome greeting message
          setMessages([
            {
              id: 'welcome',
              role: 'assistant',
              message: "Hello! I am your SkillNova AI Senior Coding Tutor. Ask me any conceptual question, framework architecture puzzle, or algorithmic question. I will explain it with simple clarity, code snippets, key points, and a practice check!",
              code_snippet: "",
              key_points: [
                "Ask anything from Python internals to React hooks or SQL performance",
                "Receive clean code snippets and mental models",
                "Test yourself with immediate micro-practice quizzes"
              ],
              practice_question: null,
            },
          ]);
        }
      } catch (err) {
        console.error('Failed to load chat history', err);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    const topic = searchParams.get('topic') || searchParams.get('query');
    if (topic) {
      setInputQuery(topic.startsWith('Explain') ? topic : `Explain ${topic} with code examples and key concepts`);
    }
  }, [searchParams]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (questionText = null) => {
    const textToSend = questionText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      message: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const response = await aiService.askAssistant(textToSend);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          message: 'Sorry, I encountered an issue processing your request. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const quickPrompts = [
    "What is inheritance in Python?",
    "Explain Python decorators with a timing example",
    "How does the React useEffect hook work?",
    "What is the difference between WHERE and HAVING in SQL?",
    "How do Django ORM select_related and prefetch_related differ?",
  ];

  return (
    <div className="fade-in" style={{ height: 'calc(100vh - var(--header-height) - 4rem)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div
        className="card"
        style={{
          padding: '1.25rem 1.75rem',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
            }}
          >
            <FiCpu />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800 }}>AI Learning Assistant</h1>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Interactive Code Tutor • Educational Mental Models • Instant Practice
            </span>
          </div>
        </div>

        <span className="badge badge-success">
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', display: 'inline-block' }} />
          Online & Ready
        </span>
      </div>

      {/* Chat Messages Stream */}
      <div
        className="card"
        style={{
          flex: 1,
          padding: '1.5rem',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          marginBottom: '1rem',
        }}
      >
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id || index}
              style={{
                display: 'flex',
                gap: '1rem',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: isUser ? '80%' : '90%',
              }}
            >
              {/* Avatar Icon */}
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  background: isUser ? 'var(--primary)' : 'var(--bg-subtle)',
                  color: isUser ? '#ffffff' : 'var(--primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  fontSize: '1.1rem',
                  border: isUser ? 'none' : '1px solid var(--border-color)',
                }}
              >
                {isUser ? <FiUser /> : <FiCpu />}
              </div>

              {/* Message Body */}
              <div
                style={{
                  background: isUser ? 'var(--primary)' : 'var(--bg-surface-elevated)',
                  color: isUser ? '#ffffff' : 'var(--text-primary)',
                  padding: '1.15rem 1.35rem',
                  borderRadius: 'var(--radius-lg)',
                  border: isUser ? 'none' : '1px solid var(--border-color)',
                  boxShadow: 'var(--shadow-sm)',
                  lineHeight: 1.6,
                  width: '100%',
                }}
              >
                {/* Text Explanation */}
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem', marginBottom: msg.code_snippet ? '1rem' : '0' }}>
                  {msg.message}
                </div>

                {/* Code Snippet Box (if provided) */}
                {msg.code_snippet && (
                  <div style={{ position: 'relative', margin: '0.85rem 0' }}>
                    <div
                      style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        zIndex: 2,
                      }}
                    >
                      <button
                        onClick={() => handleCopyCode(msg.code_snippet, index)}
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', background: 'var(--background-secondary)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
                      >
                        {copiedIndex === index ? (
                          <>
                            <FiCheck style={{ color: 'var(--success)' }} /> Copied
                          </>
                        ) : (
                          <>
                            <FiCopy /> Copy
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="code-box">
                      <code>{msg.code_snippet}</code>
                    </pre>
                  </div>
                )}

                {/* Key Points (if provided) */}
                {msg.key_points && msg.key_points.length > 0 && (
                  <div
                    style={{
                      background: 'var(--bg-subtle)',
                      padding: '0.85rem 1rem',
                      borderRadius: 'var(--radius-md)',
                      marginTop: '0.85rem',
                      fontSize: '0.875rem',
                    }}
                  >
                    <div style={{ fontWeight: 700, marginBottom: '0.4rem', color: 'var(--text-primary)' }}>
                      Key Architectural Takeaways:
                    </div>
                    <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-secondary)' }}>
                      {msg.key_points.map((pt, i) => (
                        <li key={i} style={{ marginBottom: '0.25rem' }}>{pt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Practice Question (if provided) */}
                {msg.practice_question && msg.practice_question.question && (
                  <div
                    style={{
                      border: '1px dashed var(--primary)',
                      background: 'var(--primary-light)',
                      padding: '1rem',
                      borderRadius: 'var(--radius-md)',
                      marginTop: '1rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                      <FiHelpCircle /> Mini Practice Question
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                      {msg.practice_question.question}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {msg.practice_question.options?.map((opt, optIdx) => {
                        const isChosen = userSelectedPractice[msg.id || index] === optIdx;
                        const isCorrect = optIdx === msg.practice_question.correct_option_index;

                        return (
                          <button
                            key={optIdx}
                            onClick={() => setUserSelectedPractice({ ...userSelectedPractice, [msg.id || index]: optIdx })}
                            className="btn btn-secondary btn-sm"
                            style={{
                              justifyContent: 'flex-start',
                              textAlign: 'left',
                              background: isChosen ? (isCorrect ? 'var(--success-light)' : 'var(--danger-light)') : 'var(--bg-surface)',
                              borderColor: isChosen ? (isCorrect ? 'var(--success)' : 'var(--danger)') : 'var(--border-color)',
                            }}
                          >
                            <span style={{ fontWeight: 700, marginRight: '0.4rem' }}>
                              {String.fromCharCode(65 + optIdx)}:
                            </span>
                            {opt}
                          </button>
                        );
                      })}
                    </div>

                    {userSelectedPractice[msg.id || index] !== undefined && (
                      <div style={{ marginTop: '0.75rem', fontSize: '0.825rem', color: 'var(--text-primary)' }}>
                        <strong>{userSelectedPractice[msg.id || index] === msg.practice_question.correct_option_index ? '✅ Correct! ' : '❌ Review concept: '}</strong>
                        {msg.practice_question.answer_explanation}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-muted)' }}>
            <FiCpu className="animate-spin" style={{ color: 'var(--primary)', fontSize: '1.25rem' }} />
            <span style={{ fontSize: '0.9rem' }}>SkillNova AI is reasoning and preparing code example...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Suggested Quick Queries */}
      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', marginBottom: '0.75rem', paddingBottom: '0.25rem' }}>
        {quickPrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => handleSend(p)}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: '0.78rem', whiteSpace: 'nowrap', borderRadius: 'var(--radius-full)' }}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Chat Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{
          display: 'flex',
          gap: '0.75rem',
        }}
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask a technical question (e.g. 'What is inheritance in Python?')..."
          className="form-input"
          style={{ flex: 1, padding: '0.85rem 1.25rem' }}
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="btn btn-primary"
          style={{ padding: '0 1.5rem' }}
        >
          <FiSend /> Send
        </button>
      </form>
    </div>
  );
};

export default AIAssistantPage;
