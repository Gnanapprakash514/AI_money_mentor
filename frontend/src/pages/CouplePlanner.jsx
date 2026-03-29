import React, { useState } from 'react';
import { fetchCouplePlan } from '../api/client';

const parseNumber = (value) => Number(String(value || '').replace(/,/g, '')) || 0;
const formatINR = (value) => `₹${new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(value || 0))}`;

export default function CouplePlanner() {
  const [goals, setGoals] = useState(['House']);
  const [partner1Income, setPartner1Income] = useState('');
  const [partner1Sip, setPartner1Sip] = useState('');
  const [partner2Income, setPartner2Income] = useState('');
  const [partner2Sip, setPartner2Sip] = useState('');
  const [totalFixedExpenses, setTotalFixedExpenses] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState(null);

  const toggleGoal = (g) => {
    setGoals(prev => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const p1Income = parseNumber(partner1Income);
    const p2Income = parseNumber(partner2Income);
    const p1Sip = parseNumber(partner1Sip);
    const p2Sip = parseNumber(partner2Sip);
    const fixed = parseNumber(totalFixedExpenses);
    const jointIncome = p1Income + p2Income;
    const proposedSip = Math.max(0, Math.round((jointIncome - fixed) * 0.45));
    const jointSurplus = Math.max(0, jointIncome - fixed - p1Sip - p2Sip);

    const res = await fetchCouplePlan({
      goals,
      partner1_income: p1Income,
      partner2_income: p2Income,
      partner1_sip: p1Sip,
      partner2_sip: p2Sip,
      total_fixed_expenses: fixed,
      joint_surplus: jointSurplus,
      proposed_sip: proposedSip,
    });

    setStats({ jointSurplus, proposedSip });
    setResult(res.output);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', gap: '4rem', height: '100%', padding: '0 1rem' }}>
      
      {/* LEFT FORM (45%) */}
      <form onSubmit={handleSubmit} style={{ width: '45%' }}>
        <header className="mb-8">
          <h1 style={{ fontSize: '32px' }}>The Joint Account</h1>
        </header>

        <div>
          <h3 className="font-display text-gold-300 mb-4" style={{ fontSize: '18px' }}>Partner 1</h3>
          <div className="flex gap-4 mb-4">
            <input type="text" value={partner1Income} onChange={(e) => setPartner1Income(e.target.value)} placeholder="Monthly Income" required style={{ border: 'none', borderBottom: '1px solid var(--ink-500)', width: '100%', padding: '0.5rem 0', color: 'var(--ink-100)' }} />
            <input type="text" value={partner1Sip} onChange={(e) => setPartner1Sip(e.target.value)} placeholder="Existing SIPs" style={{ border: 'none', borderBottom: '1px solid var(--ink-500)', width: '100%', padding: '0.5rem 0', color: 'var(--ink-100)' }} />
          </div>
        </div>

        <div className="mt-8">
          <h3 className="font-display text-gold-300 mb-4" style={{ fontSize: '18px' }}>Partner 2</h3>
          <div className="flex gap-4 mb-4">
            <input type="text" value={partner2Income} onChange={(e) => setPartner2Income(e.target.value)} placeholder="Monthly Income" style={{ border: 'none', borderBottom: '1px solid var(--ink-500)', width: '100%', padding: '0.5rem 0', color: 'var(--ink-100)' }} />
            <input type="text" value={partner2Sip} onChange={(e) => setPartner2Sip(e.target.value)} placeholder="Existing SIPs" style={{ border: 'none', borderBottom: '1px solid var(--ink-500)', width: '100%', padding: '0.5rem 0', color: 'var(--ink-100)' }} />
          </div>
        </div>

        <div className="mt-8">
          <h3 className="font-display text-gold-300 mb-4" style={{ fontSize: '18px' }}>Together</h3>
          <div className="flex gap-4 mb-6" style={{ flexWrap: 'wrap' }}>
            {['House', 'Child Ed.', 'FIRE at 50', 'Vacations'].map(g => {
              const active = goals.includes(g);
              return (
                <button 
                  type="button" 
                  key={g} 
                  onClick={() => toggleGoal(g)}
                  style={{
                    border: '1px solid var(--gold-500)',
                    background: active ? 'var(--gold-500)' : 'transparent',
                    color: active ? 'var(--ember-900)' : 'var(--ink-100)',
                    padding: '0.4rem 1rem',
                    borderRadius: '2px',
                    fontSize: '14px'
                  }}
                >
                  {g}
                </button>
              );
            })}
          </div>
          <input type="text" value={totalFixedExpenses} onChange={(e) => setTotalFixedExpenses(e.target.value)} placeholder="Total Fixed Expenses" required style={{ border: 'none', borderBottom: '1px solid var(--ink-500)', width: '100%', padding: '0.5rem 0', color: 'var(--ink-100)', marginBottom: '2rem' }} />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full font-display" 
          style={{ background: 'var(--gold-500)', color: 'var(--ember-900)', border: 'none', fontSize: '16px', padding: '1rem', borderRadius: '2px', cursor: 'pointer', transition: 'opacity 0.2s' }}
        >
          {loading ? "Calculating..." : "Generate Our Plan →"}
        </button>
      </form>

      {/* RIGHT RESULTS (55%) */}
      <div className="panel" style={{ width: '55%', minHeight: '600px', display: 'flex', flexDirection: 'column' }}>
        {!result ? (
           <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
             <p className="font-display text-ink-500" style={{ fontSize: '20px', fontStyle: 'italic', textAlign: 'center' }}>Your joint plan will appear here.</p>
           </div>
        ) : (
           <div className="fade-in" style={{ padding: '2rem' }}>
             {/* 4 Stat Boxes */}
             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
               <div style={{ border: '1px solid rgba(201,146,42,0.15)', padding: '1.5rem', borderRadius: '2px' }}>
                 <div className="font-mono text-ink-500 mb-2" style={{ fontSize: '0.7rem', letterSpacing: '1px' }}>JOINT SURPLUS</div>
                 <div className="font-display text-gold-300" style={{ fontSize: '28px' }}>{formatINR(stats?.jointSurplus)}</div>
               </div>
               <div style={{ border: '1px solid rgba(201,146,42,0.15)', padding: '1.5rem', borderRadius: '2px' }}>
                 <div className="font-mono text-ink-500 mb-2" style={{ fontSize: '0.7rem', letterSpacing: '1px' }}>PROPOSED SIP</div>
                 <div className="font-display text-gold-300" style={{ fontSize: '28px' }}>{formatINR(stats?.proposedSip)}</div>
               </div>
             </div>

             {/* AI Plan Text */}
             <div className="text-ink-300" style={{ fontSize: '14px', lineHeight: 1.6 }}>
               <p style={{ whiteSpace: 'pre-wrap' }}>{result}</p>
             </div>
           </div>
        )}
      </div>

    </div>
  );
}
