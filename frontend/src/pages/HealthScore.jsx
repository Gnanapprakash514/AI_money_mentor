import React, { useEffect, useState } from 'react';
import { fetchHealthScore, fetchSavedProfile, getStoredProfile } from '../api/client';

const getColor = (val) => {
  if (val <= 40) return 'var(--signal-red)';
  if (val <= 70) return 'var(--gold-500)';
  return 'var(--signal-green)';
};

export default function HealthScore() {
  const [actualScore, setActualScore] = useState(0);
  const [scoreDisplay, setScoreDisplay] = useState(0);
  const [profile, setProfile] = useState(getStoredProfile());
  const [healthNarrative, setHealthNarrative] = useState('');

  useEffect(() => {
    fetchSavedProfile().then(setProfile).catch(() => undefined);
    fetchHealthScore({}).then(res => {
      setActualScore(res.score || 72);
      setHealthNarrative(res.output || '');
    });
  }, []);

  const emergencyMonths = Number(profile?.risk_profile?.emergency_fund_months || 0);
  const savingsRate = Number(profile?.derived?.savings_rate_percent || 0);
  const emiRatio = Number(profile?.derived?.emi_to_income_ratio || 0);
  const equityValue = Number(profile?.assets?.stocks || 0) + Number(profile?.assets?.mutual_funds_value || 0);
  const totalAssets = Number(profile?.assets?.total_assets || 0);
  const equityAllocation = totalAssets > 0 ? (equityValue / totalAssets) * 100 : 0;
  const insuranceCover = Number(profile?.insurance?.life_cover || 0) + Number(profile?.insurance?.health_cover || 0);
  const goalYears = Number(profile?.goals?.[0]?.years_remaining || 10);

  const dimensions = [
    {
      name: 'Emergency Buffer',
      val: Math.min(100, Math.round((emergencyMonths / 6) * 100)),
      comment: `Runway: ${emergencyMonths.toFixed(1)} months. Target is 6+ months.`
    },
    {
      name: 'Savings Rate',
      val: Math.min(100, Math.round((savingsRate / 35) * 100)),
      comment: `Current savings rate: ${savingsRate.toFixed(1)}%. Aim for 30%+.`
    },
    {
      name: 'Debt Servicing',
      val: Math.max(0, Math.min(100, Math.round(100 - emiRatio * 3))),
      comment: `EMI-to-income ratio: ${emiRatio.toFixed(1)}%. Lower is better.`
    },
    {
      name: 'Equity Allocation',
      val: Math.min(100, Math.round(equityAllocation)),
      comment: `Equity share in assets: ${equityAllocation.toFixed(1)}%.`
    },
    {
      name: 'Insurance Cover',
      val: Math.min(100, Math.round((insuranceCover / 5000000) * 100)),
      comment: `Combined cover: ₹${Math.round(insuranceCover).toLocaleString('en-IN')}.`
    },
    {
      name: 'Goal Velocity',
      val: Math.max(20, Math.min(100, Math.round(100 - goalYears * 5))),
      comment: `Primary goal timeline: ${goalYears} years remaining.`
    }
  ];

  useEffect(() => {
    if (actualScore === 0) return;
    
    let current = 0;
    const duration = 1200; // ms
    const increment = actualScore / (duration / 16); 
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= actualScore) {
        setScoreDisplay(actualScore);
        clearInterval(timer);
      } else {
        setScoreDisplay(Math.floor(current));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [actualScore]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      
      <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center' }}>
          <span className="font-display score-value" style={{ fontSize: '120px', lineHeight: 1 }}>{scoreDisplay}</span>
          <span className="font-mono text-ink-500" style={{ fontSize: '40px', marginLeft: '0.5rem' }}>/100</span>
        </div>
        <div className="font-mono text-ink-500" style={{ fontSize: '0.7rem', letterSpacing: '3px', marginTop: '1rem' }}>
          YOUR MONEY PORTRAIT
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '2rem',
        maxWidth: '900px',
        width: '100%'
      }}>
        {dimensions.map((dim, i) => (
          <div key={i} className="card" style={{ 
            padding: '1.5rem', 
            border: '1px solid rgba(201,146,42,0.1)'
          }}>
            <h3 className="font-display" style={{ fontSize: '16px', marginBottom: '0.5rem' }}>{dim.name}</h3>
            <p className="text-ink-300" style={{ fontSize: '13px', lineHeight: 1.5, minHeight: '40px' }}>{dim.comment}</p>
            <div style={{ height: '3px', background: 'var(--ember-600)', width: '100%', marginTop: '1rem' }}>
              <div style={{ 
                height: '100%', 
                width: `${scoreDisplay === actualScore ? dim.val : 0}%`, 
                background: getColor(dim.val),
                transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)'
              }}></div>
            </div>
          </div>
        ))}
      </div>

      {healthNarrative && (
        <div className="panel mt-8" style={{ padding: '1rem', width: '100%', maxWidth: '900px' }}>
          <h3 className="font-display mb-3" style={{ fontSize: '18px' }}>AI Health Commentary</h3>
          <p className="text-ink-300" style={{ whiteSpace: 'pre-wrap' }}>{healthNarrative}</p>
        </div>
      )}

    </div>
  );
}
