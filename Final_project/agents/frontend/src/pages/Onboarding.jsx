import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { startOnboarding, submitOnboardingMessage } from '../api/client';

export default function Onboarding() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, loading, complete]);

  useEffect(() => {
    let cancelled = false;
    startOnboarding().then((res) => {
      if (!cancelled) {
        setHistory([{ type: 'bot', text: res.reply }]);
        setProgress(res.progress || 0);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!inputVal.trim() || loading) return;

    const newHistory = [...history, { type: 'user', text: inputVal.trim() }];
    setHistory(newHistory);
    setInputVal('');
    setLoading(true);

    const res = await submitOnboardingMessage(inputVal.trim(), newHistory);
    setProgress(res.progress || 0);

    if (res.done) {
      setLoading(false);
      setComplete(true);
      return;
    }

    setHistory([...newHistory, { type: 'bot', text: res.reply }]);
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (complete) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-ember-900" style={{ padding: '2rem' }}>
        <div className="fade-in" style={{ maxWidth: '640px', width: '100%', textAlign: 'center' }}>
          <div className="font-mono text-gold-500 mb-8" style={{ fontSize: '0.6rem', letterSpacing: '4px' }}>AI MONEY MENTOR</div>
          <h1 className="mb-4" style={{ fontSize: '36px' }}>Profile Established</h1>
          <p className="text-ink-300 font-mono mb-8" style={{ fontSize: '0.9rem' }}>ONBOARDING: {progress}% COMPLETE</p>
          <div className="panel" style={{ padding: '2rem', textAlign: 'left', marginBottom: '2rem' }}>
            <h3 className="font-display text-ink-100 mb-4" style={{ fontSize: '20px' }}>Top Actions</h3>
            <ul className="text-ink-300 font-mono" style={{ listStyle: 'none', lineHeight: 2, fontSize: '0.85rem' }}>
              <li>&rarr; Maximize 80C Limits</li>
              <li>&rarr; Establish 6-Month Emergency Buffer</li>
              <li>&rarr; Accelerate Auto Loan Repayment</li>
            </ul>
          </div>
          <button className="btn-primary font-mono" onClick={() => navigate('/')}>PROCEED TO DASHBOARD &rarr;</button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center min-h-screen bg-ember-900" style={{ padding: '4rem 2rem' }}>
      <div style={{ maxWidth: '640px', width: '100%' }}>
        
        <div className="font-mono text-gold-500 mb-12" style={{ fontSize: '0.6rem', letterSpacing: '4px', textAlign: 'center' }}>AI MONEY MENTOR</div>

        {/* History Stream */}
        <div style={{ paddingBottom: '2rem' }}>
          {history.map((msg, i) => {
            const isLatest = i === history.length - 1;
            const opacity = isLatest ? 1 : Math.max(0.2, 1 - (history.length - i) * 0.15);
            return (
              <div key={i} className={isLatest ? "fade-in" : ""} style={{ opacity, marginBottom: '2rem' }}>
                {msg.type === 'bot' ? (
                   <h2 className="font-display" style={{ fontSize: '28px', color: 'var(--ink-100)' }}>{msg.text}</h2>
                ) : (
                   <p className="font-display" style={{ fontSize: '20px', color: 'var(--ink-300)', fontStyle: 'italic', textAlign: 'right' }}>"{msg.text}"</p>
                )}
              </div>
            );
          })}
          
          {loading && (
            <div className="font-display pulse" style={{ fontSize: '28px', color: 'var(--ink-100)' }}>...</div>
          )}
        </div>

        {/* Input Zone */}
        {!loading && (
          <form onSubmit={handleSubmit} className="flex flex-col mt-4 fade-in relative">
            <textarea 
              autoFocus
              className="font-display"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Your answer..."
              rows={1}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                borderBottom: '1px solid var(--gold-500)',
                color: 'var(--ink-100)',
                fontSize: '20px',
                fontStyle: 'italic',
                padding: '0.5rem 0',
                resize: 'none',
                overflow: 'hidden'
              }}
            />
            {inputVal.trim() && (
              <button type="submit" className="font-mono text-gold-500 mt-4" style={{ background: 'transparent', border: 'none', textAlign: 'right', fontSize: '0.85rem' }}>
                CONTINUE &rarr;
              </button>
            )}
          </form>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
