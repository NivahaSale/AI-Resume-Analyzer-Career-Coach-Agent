import React, { useState, useRef, useEffect } from 'react';

const MockInterview = () => {
  const [mode, setMode] = useState('technical');
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  
  const [isChatActive, setIsChatActive] = useState(false);
  const [history, setHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState('');
  
  // Audio state
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceURI, setSelectedVoiceURI] = useState('');
  const recognitionRef = useRef(null);

  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const loadVoices = () => {
      const rawVoices = window.speechSynthesis.getVoices();
      const enVoices = rawVoices.filter(v => v.lang.startsWith('en-'));
      setAvailableVoices(enVoices);
      
      if (enVoices.length > 0 && !selectedVoiceURI) {
        // Try to favor natural sounding voices if available natively
        const preferred = enVoices.find(v => v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Natural')) || enVoices[0];
        setSelectedVoiceURI(preferred.voiceURI);
      }
    };

    loadVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, [selectedVoiceURI]);

  useEffect(() => {
    scrollToBottom();
  }, [history, isTyping]);

  useEffect(() => {
    // Setup Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setCurrentMessage(prev => prev + (prev.endsWith(' ') || prev === '' ? '' : ' ') + transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
    
    // Cleanup on unmount
    return () => {
      window.speechSynthesis.cancel();
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setError("Speech recognition is not supported in this browser.");
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error("Speech Recognition failed to start", e);
      }
    }
  };

  const speakText = (text) => {
    // If the interview is actively open, let's play the voice
    if (!isAudioEnabled) return;
    
    window.speechSynthesis.cancel(); // Cancel any ongoing speech
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    if (selectedVoiceURI) {
      const voices = window.speechSynthesis.getVoices();
      const chosenVoice = voices.find(v => v.voiceURI === selectedVoiceURI);
      if (chosenVoice) utterance.voice = chosenVoice;
    }
    
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    } else {
      setFile(null);
    }
  };

  const handleStart = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload a resume file first.');
      return;
    }
    setError('');
    setIsChatActive(true);
    // Trigger initial question securely
    await sendMessage("Hello! I am ready to start the interview.", true);
  };

  const sendMessage = async (messageText, isInitialCall = false) => {
    if (!messageText.trim() && !isInitialCall) return;

    window.speechSynthesis.cancel(); // Cancel speech if user interrupts by sending

    let updatedHistory = [...history];
    if (!isInitialCall) {
      updatedHistory = [...history, { role: 'user', content: messageText }];
      setHistory(updatedHistory);
      setCurrentMessage('');
    }
    
    // Ensure we stop recording when sending
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }
    
    setIsTyping(true);
    setError('');

    const formData = new FormData();
    formData.append('mode', mode);
    formData.append('resume', file);
    if (jd.trim()) formData.append('job_description', jd);
    if (messageText.trim()) formData.append('message', messageText);
    
    const historyToSend = isInitialCall ? [] : history;
    if (historyToSend.length > 0) {
      formData.append('history', JSON.stringify(historyToSend));
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/interview/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with AI recruiter. Check connection.');
      }

      const data = await response.json();
      const aiReply = data.reply;
      
      setHistory([...updatedHistory, { role: 'ai', content: aiReply }]);
      
      // Attempt TTS read out loudly
      speakText(aiReply);
    } catch (err) {
      setError(err.message || 'An error occurred during the interview.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(currentMessage);
    }
  };

  const handleReset = () => {
    window.speechSynthesis.cancel();
    if (isListening && recognitionRef.current) {
      recognitionRef.current.abort();
      setIsListening(false);
    }
    setIsChatActive(false);
    setHistory([]);
    setCurrentMessage('');
    setError('');
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', width: '100%', padding: '1rem 0', height: '100%' }}>
      <style>{`
        @keyframes typingBounce {
          0%, 100% { transform: translateY(0); opacity: 0.4; }
          50% { transform: translateY(-4px); opacity: 1; }
        }
        .typing-dot {
          width: 8px;
          height: 8px;
          background-color: var(--color-cyan);
          border-radius: 50%;
          animation: typingBounce 1.4s infinite ease-in-out both;
        }
        @keyframes micPulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `}</style>

      {!isChatActive ? (
        <div className="card mb-4 animate-fade-in" style={{ width: '100%', maxWidth: '650px', alignSelf: 'flex-start' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.6rem' }}>Configure Mock Interview</h2>
          <p className="text-secondary mb-4" style={{ lineHeight: '1.6' }}>
            Choose your interview persona, upload your resume, and optionally provide a job description to tailor the interview.
          </p>

          <form onSubmit={handleStart}>
            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Interview Type</label>
              <select 
                className="form-control" 
                value={mode} 
                onChange={(e) => setMode(e.target.value)}
                style={{
                  backgroundColor: 'rgba(11, 15, 26, 0.6)',
                  padding: '0.85rem 1rem',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  appearance: 'auto',
                  fontSize: '0.95rem'
                }}
              >
                <option value="technical" style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>Technical / Coding</option>
                <option value="hr" style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>HR Screening</option>
                <option value="manager" style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)' }}>Hiring Manager Fit</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Resume (PDF or DOCX)</label>
              <input 
                type="file" 
                className="form-control" 
                onChange={handleFileChange} 
                accept=".pdf,.doc,.docx" 
                required
                style={{
                  backgroundColor: 'rgba(11, 15, 26, 0.6)',
                  padding: '0.75rem 1rem',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  width: '100%',
                  cursor: 'pointer',
                  fontSize: '0.95rem'
                }}
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>Job Description (Optional)</label>
              <textarea 
                className="form-control" 
                rows="4" 
                placeholder="Paste the job description here to heavily tailor the interview questions."
                value={jd}
                onChange={(e) => setJd(e.target.value)}
                style={{ resize: 'vertical', fontSize: '0.95rem', padding: '1rem' }}
              />
            </div>

            {error && <p style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</p>}

            <button 
              type="submit"
              className="btn w-full text-primary" 
              style={{ 
                marginTop: '0.5rem', 
                padding: '1rem',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                borderRadius: '8px',
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: '600',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
            >
              Start Interview
            </button>
          </form>
        </div>
      ) : (
        <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '900px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', padding: '0', overflow: 'hidden' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'rgba(11, 15, 26, 0.5)' }}>
            <div>
              <h2 className="text-gradient" style={{ margin: 0, fontSize: '1.4rem' }}>Live Mock Interview</h2>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Persona: {mode.toUpperCase()}</span>
            </div>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              {isAudioEnabled && availableVoices.length > 0 && (
                <select
                  value={selectedVoiceURI}
                  onChange={(e) => setSelectedVoiceURI(e.target.value)}
                  style={{
                    backgroundColor: 'rgba(11, 15, 26, 0.6)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: 'var(--text-secondary)',
                    padding: '0.4rem 0.6rem',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    maxWidth: '180px',
                    cursor: 'pointer',
                    outline: 'none'
                  }}
                  title="Select AI Voice"
                >
                  {availableVoices.map(v => (
                    <option key={v.voiceURI} value={v.voiceURI}>{v.name}</option>
                  ))}
                </select>
              )}
              <button 
                className="btn btn-outline"
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  backgroundColor: !isAudioEnabled ? 'rgba(239, 68, 68, 0.1)' : 'transparent',
                  borderColor: !isAudioEnabled ? 'rgba(239, 68, 68, 0.5)' : 'var(--border-color)',
                  color: !isAudioEnabled ? '#ef4444' : 'var(--text-primary)'
                }}
                onClick={() => {
                  if (isAudioEnabled) window.speechSynthesis.cancel();
                  setIsAudioEnabled(!isAudioEnabled);
                }}
              >
                {isAudioEnabled ? '🔊 AI Voice On' : '🔇 AI Voice Off'}
              </button>
              <button 
                className="btn btn-outline" 
                onClick={handleReset}
                style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
              >
                End Interview
              </button>
            </div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {history.length === 0 && isTyping && (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '2rem' }}>
                <div style={{ marginBottom: '1rem', fontSize: '2rem' }}>🎙️</div>
                <p>The recruiter is reviewing your resume and preparing...</p>
              </div>
            )}
            
            {history.map((msg, idx) => (
              <div key={idx} className="animate-fade-in" style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                width: '100%'
              }}>
                <span style={{ 
                  fontSize: '0.8rem', 
                  color: 'var(--text-muted)', 
                  marginBottom: '0.4rem',
                  marginLeft: msg.role === 'ai' ? '0.5rem' : '0',
                  marginRight: msg.role === 'user' ? '0.5rem' : '0',
                  fontWeight: '600'
                }}>
                  {msg.role === 'user' ? 'You' : 'AI Recruiter'}
                </span>
                <div style={{
                  maxWidth: '85%',
                  padding: '1rem 1.2rem',
                  borderRadius: '16px',
                  backgroundColor: msg.role === 'user' ? 'var(--color-blue)' : 'rgba(26, 33, 56, 0.6)',
                  color: msg.role === 'user' ? '#ffffff' : 'var(--text-primary)',
                  borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                  borderBottomLeftRadius: msg.role === 'ai' ? '4px' : '16px',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  border: msg.role === 'ai' ? '1px solid rgba(255,255,255,0.05)' : 'none',
                  boxShadow: '0 4px 10px rgba(0,0,0,0.15)'
                }}>
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isTyping && history.length > 0 && (
              <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.5rem', marginBottom: '0.4rem', fontWeight: '600' }}>AI Recruiter</span>
                <div style={{
                  padding: '1.2rem 1.5rem',
                  borderRadius: '16px',
                  borderBottomLeftRadius: '4px',
                  backgroundColor: 'rgba(26, 33, 56, 0.6)',
                  display: 'flex',
                  gap: '0.5rem',
                  alignItems: 'center',
                  boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <div className="typing-dot"></div>
                  <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                  <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', backgroundColor: 'rgba(11, 15, 26, 0.4)' }}>
            {error && <p style={{ color: '#ef4444', marginBottom: '1rem', textAlign: 'center' }}>{error}</p>}
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
                <textarea 
                  className="form-control"
                  placeholder="Type your answer or click the mic to speak..."
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  disabled={isTyping}
                  style={{ 
                    flex: 1, 
                    resize: 'none', 
                    borderRadius: '8px', 
                    padding: '1rem',
                    paddingRight: '4rem',
                    backgroundColor: isTyping ? 'rgba(255,255,255,0.02)' : 'rgba(11, 15, 26, 0.8)',
                    color: isTyping ? 'var(--text-muted)' : 'var(--text-primary)',
                    height: '60px',
                    minHeight: '60px',
                    border: isTyping ? '1px solid rgba(255,255,255,0.05)' : '1px solid var(--border-color)'
                  }}
                />
                <div style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  display: 'flex',
                  alignItems: 'center',
                  background: isListening ? 'rgba(239, 68, 68, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  border: isListening ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '50%',
                  padding: '8px',
                  cursor: isTyping ? 'not-allowed' : 'pointer',
                  animation: isListening ? 'micPulse 1.5s infinite' : 'none',
                  transition: 'all 0.2s ease',
                  opacity: isTyping ? 0.5 : 1
                }}
                onClick={!isTyping ? toggleListening : undefined}
                title={isListening ? "Stop listening" : "Start dictation"}
                >
                  <span style={{ fontSize: '1.2rem', filter: isListening ? 'grayscale(0%)' : 'grayscale(100%)' }}>
                    🎤
                  </span>
                </div>
              </div>
              
              <button 
                className="btn btn-primary"
                onClick={() => sendMessage(currentMessage)}
                disabled={isTyping || (!currentMessage.trim() && !isListening)}
                style={{ padding: '0 2rem', borderRadius: '8px', alignSelf: 'stretch', opacity: (isTyping || (!currentMessage.trim() && !isListening)) ? 0.5 : 1 }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MockInterview;
