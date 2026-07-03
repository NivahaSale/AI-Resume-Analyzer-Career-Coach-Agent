import React, { useState } from 'react';

const MentoringMode = () => {
  const [file, setFile] = useState(null);
  const [targetRole, setTargetRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [learningPreferences, setLearningPreferences] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    } else {
      setFile(null);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    if (file) formData.append('resume', file);
    if (targetRole.trim()) formData.append('target_role', targetRole);
    if (experienceLevel.trim()) formData.append('experience_level', experienceLevel);
    if (learningPreferences.trim()) formData.append('learning_preferences', learningPreferences);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/mentoring', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate mentoring roadmap. Please check the backend connection.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred while generating the roadmap.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
      {/* Left Column: Input Form */}
      <div style={{ flex: '1 1 400px' }}>
        <div className="card mb-4 animate-fade-in">
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Mentoring Mode</h2>
          <p className="text-secondary mb-4">
            Share your current context and goals. The backend mentoring agents will
            generate a learning-focused roadmap (LLM logic is currently stubbed).
          </p>

          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Optional resume upload</label>
              <input 
                type="file" 
                className="form-control" 
                onChange={handleFileChange} 
                accept=".pdf,.doc,.docx" 
                style={{
                  backgroundColor: 'rgba(11, 15, 26, 0.6)',
                  padding: '0.75rem 1rem',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  width: '100%',
                  cursor: 'pointer'
                }}
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Target role</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. ML Engineer"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Experience level</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. Junior"
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Learning preferences</label>
              <textarea 
                className="form-control" 
                rows="4" 
                placeholder="Describe how you prefer to learn (projects, courses, pair programming, etc.)."
                value={learningPreferences}
                onChange={(e) => setLearningPreferences(e.target.value)}
                style={{ resize: 'vertical' }}
              />
            </div>

            {error && <p style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</p>}

            <button 
              type="submit"
              className="btn btn-primary w-full" 
              disabled={loading}
              style={{ marginTop: '0.5rem', padding: '1rem' }}
            >
              {loading ? 'Generating Roadmap...' : 'Generate Mentoring Roadmap'}
            </button>
          </form>
        </div>
      </div>

      {/* Right Column: Results */}
      <div style={{ flex: '1 1 500px' }}>
        {loading && (
          <div className="card animate-fade-in flex justify-center items-center" style={{ minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p className="text-gradient" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Designing roadmap...</p>
          </div>
        )}

        {result && !loading && (
          <div className="card animate-fade-in" style={{ backgroundColor: '#f3f4f6', color: '#1f2937', padding: '2.5rem' }}>
            <h3 style={{ color: '#111827', marginBottom: '1.5rem', fontSize: '1.4rem' }}>Improvement Roadmap</h3>
            <p style={{ color: '#4b5563', lineHeight: '1.6', marginBottom: '3rem' }}>
              {result.overview}
            </p>

            {/* Timeline UI */}
            <div style={{ position: 'relative', paddingLeft: '3rem', paddingBottom: '2rem' }}>
              {/* Vertical line connecting nodes */}
              <div style={{
                position: 'absolute',
                top: '2rem',
                bottom: '1rem',
                left: '11px',
                width: '3px',
                backgroundColor: '#111827'
              }}></div>

              {result.entries && result.entries.map((entry, idx) => (
                <div key={idx} style={{ position: 'relative', marginBottom: '3rem' }}>
                  {/* Timeline dot */}
                  <div style={{
                    position: 'absolute',
                    left: '-3rem',
                    top: '2rem',
                    width: '16px',
                    height: '16px',
                    backgroundColor: idx % 2 === 0 ? '#ef4444' : '#8b5cf6',
                    border: '3px solid #f3f4f6',
                    borderRadius: '50%',
                    zIndex: 2,
                    transform: 'translateX(3px)'
                  }}></div>
                  
                  {/* Connecting horizontal line segment */}
                  <div style={{
                    position: 'absolute',
                    left: '-3rem',
                    top: '2rem',
                    width: '3rem',
                    height: '2px',
                    backgroundColor: idx % 2 === 0 ? '#ef4444' : '#8b5cf6',
                    marginTop: '6px',
                    zIndex: 1,
                    transform: 'translateX(7px)'
                  }}></div>

                  <div style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    width: '75%',
                    marginLeft: idx % 2 === 0 ? '0' : '25%'
                  }}>
                    <h4 style={{ color: '#111827', marginBottom: '0.5rem', fontSize: '1.15rem' }}>{entry.skill}</h4>
                    <span style={{ 
                      backgroundColor: '#e5e7eb', 
                      color: '#4b5563',
                      padding: '0.3rem 0.8rem',
                      borderRadius: '20px',
                      fontSize: '0.8rem',
                      fontWeight: '600',
                      display: 'inline-block',
                      marginBottom: '1rem'
                    }}>
                      {entry.timeline}
                    </span>
                    <p style={{ color: '#6b7280', fontSize: '0.95rem', margin: 0, lineHeight: '1.6' }}>
                      {entry.project}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MentoringMode;
