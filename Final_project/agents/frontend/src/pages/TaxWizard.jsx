import React, { useEffect, useState } from 'react';
import { fetchSavedProfile, fetchTax, getStoredProfile } from '../api/client';

const formatINR = (value) => `₹${new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(value || 0))}`;

export default function TaxWizard() {
  const [taxInsight, setTaxInsight] = useState('');
  const [profile, setProfile] = useState(getStoredProfile());

  useEffect(() => {
    fetchTax({}).then((res) => setTaxInsight(res.output || ''));
    fetchSavedProfile().then(setProfile).catch(() => undefined);
  }, []);

  const grossAnnual = Number(profile?.income?.monthly_take_home || 0) * 12 + Number(profile?.income?.annual_bonus || 0);
  const sec80c = Math.min(150000, Number(profile?.assets?.ppf || 0) + Number(profile?.assets?.epf || 0));
  const sec80d = Math.min(50000, Number(profile?.insurance?.health_cover || 0) > 0 ? 50000 : 0);
  const oldTax = Math.max(0, Math.round(grossAnnual * 0.18 - sec80c * 0.1 - sec80d * 0.1));
  const newTax = Math.max(0, Math.round(grossAnnual * 0.14));
  const savings = Math.max(0, oldTax - newTax);

  return (
    <div style={{ padding: '0 1rem', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Top Drag Drop Zone */}
      <div 
        className="mb-8 radius-sm" 
        style={{ 
          border: '1px dashed rgba(201,146,42,0.4)', 
          padding: '3rem', 
          textAlign: 'center',
          transition: 'all 0.3s ease',
          background: 'rgba(22,18,13,0.5)'
        }}
        onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(201,146,42,1)'}
        onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(201,146,42,0.4)'}
      >
        <div className="font-mono text-ink-500" style={{ letterSpacing: '2px' }}>DROP FORM 16 HERE</div>
      </div>

      <div className="flex gap-4" style={{ columnGap: '3rem' }}>
        
        {/* Left Column: The Ledger */}
        <div className="w-full">
          <header className="mb-6">
            <h1 style={{ fontSize: '28px' }}>The Ledger</h1>
          </header>

          <div className="flex gap-4">
            {/* Old Regime */}
            <div className="w-full panel" style={{ padding: '1.5rem' }}>
              <h3 className="font-display mb-4" style={{ fontSize: '18px', borderBottom: '1px solid rgba(201,146,42,0.15)', paddingBottom: '0.5rem' }}>Old Regime</h3>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Gross</span><span>{formatINR(grossAnnual)}</span>
              </div>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Std. Ded</span><span>-₹50,000</span>
              </div>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Sec 80C</span><span>-{formatINR(sec80c)}</span>
              </div>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Sec 80D</span><span>-{formatINR(sec80d)}</span>
              </div>
              <div className="flex justify-between mt-6">
                <span className="font-mono text-ink-500">Tax Payable</span>
                <span className="font-display text-ink-100" style={{ fontSize: '24px' }}>{formatINR(oldTax)}</span>
              </div>
            </div>

            {/* New Regime */}
            <div className="w-full panel" style={{ padding: '1.5rem' }}>
              <h3 className="font-display mb-4" style={{ fontSize: '18px', borderBottom: '1px solid rgba(201,146,42,0.15)', paddingBottom: '0.5rem' }}>New Regime</h3>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Gross</span><span>{formatINR(grossAnnual)}</span>
              </div>
              <div className="flex justify-between font-mono text-ink-300 py-2 border-b-ink">
                <span>Std. Ded</span><span>-₹75,000</span>
              </div>
              <div className="flex justify-between font-mono text-ink-500 py-2 border-b-ink" style={{ opacity: 0.5 }}>
                <span>Sec 80C</span><span>N/A</span>
              </div>
              <div className="flex justify-between font-mono text-ink-500 py-2 border-b-ink" style={{ opacity: 0.5 }}>
                <span>Sec 80D</span><span>N/A</span>
              </div>
              <div className="flex justify-between mt-6">
                <span className="font-mono text-ink-500">Tax Payable</span>
                <span className="font-display text-gold-500" style={{ fontSize: '24px' }}>{formatINR(newTax)}</span>
              </div>
            </div>
          </div>

          <div className="w-full mt-6" style={{ background: 'var(--ember-800)', border: '1px solid rgba(201,146,42,0.15)', padding: '1rem', textAlign: 'center' }}>
            <span className="font-mono text-signal-green" style={{ letterSpacing: '1px' }}>NEW REGIME SAVES {formatINR(savings)}</span>
          </div>
        </div>

        {/* Right Column: Untapped Deductions */}
        <div className="w-full" style={{ maxWidth: '350px' }}>
          <header className="mb-6">
            <h2 className="font-display" style={{ fontSize: '20px' }}>Untapped Deductions</h2>
          </header>

          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <span className="font-display" style={{ fontSize: '16px' }}>Section 80C</span>
              <span className="font-mono text-signal-red" style={{ fontSize: '12px' }}>₹50k Gap</span>
            </div>
            <div style={{ height: '3px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: '66%', background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500 flex justify-between" style={{ fontSize: '12px' }}>
              <span>Used: ₹1.0L</span><span>Limit: ₹1.5L</span>
            </div>
            <p className="text-ink-300 mt-2" style={{ fontSize: '13px', lineHeight: 1.4 }}>Funnel this gap into ELSS to maximize old regime returns if you shift.</p>
          </div>

          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <span className="font-display" style={{ fontSize: '16px' }}>Section 80D (Health)</span>
              <span className="font-mono text-signal-red" style={{ fontSize: '12px' }}>₹25k Gap</span>
            </div>
            <div style={{ height: '3px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: '50%', background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500 flex justify-between" style={{ fontSize: '12px' }}>
              <span>Used: ₹25k</span><span>Limit: ₹50k</span>
            </div>
            <p className="text-ink-300 mt-2" style={{ fontSize: '13px', lineHeight: 1.4 }}>Parental health insurance premiums are fully deductible here.</p>
          </div>

          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <span className="font-display" style={{ fontSize: '16px' }}>NPS (80CCD)</span>
              <span className="font-mono text-signal-red" style={{ fontSize: '12px' }}>₹50k Gap</span>
            </div>
            <div style={{ height: '3px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: '0%', background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500 flex justify-between" style={{ fontSize: '12px' }}>
              <span>Used: ₹0</span><span>Limit: ₹50k</span>
            </div>
            <p className="text-ink-300 mt-2" style={{ fontSize: '13px', lineHeight: 1.4 }}>Exclusive deduction available over and above 80C.</p>
          </div>

        </div>
      </div>

      {taxInsight && (
        <div className="panel mt-6" style={{ padding: '1rem' }}>
          <h3 className="font-display mb-3" style={{ fontSize: '18px' }}>AI Tax Insight</h3>
          <p className="text-ink-300" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
            {taxInsight}
          </p>
        </div>
      )}
    </div>
  );
}
