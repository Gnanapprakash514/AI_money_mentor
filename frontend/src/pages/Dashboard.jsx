import React, { useEffect, useState } from 'react';
import { fetchFeed, fetchSavedProfile, getStoredProfile } from '../api/client';

const formatINR = (value) =>
  new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(value || 0));

const toCr = (value) => `${(Number(value || 0) / 10000000).toFixed(2)}Cr`;

const goalProgress = (goal) => {
  if (!goal) return 0;
  const target = Number(goal.target_amount || 0);
  if (target <= 0) return 0;
  const current = target * 0.25;
  return Math.max(0, Math.min(100, Math.round((current / target) * 100)));
};

export default function Dashboard() {
  const [feed, setFeed] = useState(null);
  const [profile, setProfile] = useState(getStoredProfile());

  useEffect(() => {
    fetchFeed().then(res => setFeed(res.output));
    fetchSavedProfile().then(setProfile).catch(() => undefined);
  }, []);

  const retirementTarget = Number(profile?.expenses?.monthly_total || 0) * 12 * 25;
  const retirementCurrent = Number(profile?.assets?.total_assets || 0);
  const retirementPct = retirementTarget > 0 ? Math.min(100, Math.round((retirementCurrent / retirementTarget) * 100)) : 0;
  const primaryGoal = profile?.goals?.[0];
  const goalPct = goalProgress(primaryGoal);
  const goalCurrent = primaryGoal ? Number(primaryGoal.target_amount || 0) * (goalPct / 100) : 0;
  const monthlySip = Number(profile?.assets?.monthly_sip || 0);
  const monthlySurplus = Number(profile?.derived?.monthly_surplus || 0);

  return (
    <div style={{ padding: '0 1rem' }}>
      <header className="mb-8" style={{ borderBottom: '2px solid var(--ink-100)', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '3rem', letterSpacing: '-1px', lineHeight: 1.1 }}>The Morning Briefing</h1>
        <p className="font-mono text-ink-300" style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>EDITION 402 • VOL. IV</p>
      </header>

      {feed && (
        <div className="panel mb-8" style={{ padding: '1rem' }}>
          <h3 className="font-display mb-2" style={{ fontSize: '18px' }}>AI Generated Daily Feed</h3>
          <p className="text-ink-300" style={{ whiteSpace: 'pre-wrap' }}>{feed}</p>
        </div>
      )}

      <div className="dashboard-grid">
        {/* LEFT COLUMN: Feed */}
        <section>
          <h3 className="font-mono text-ink-500 mb-4" style={{ fontSize: '0.9rem', letterSpacing: '2px', borderBottom: '1px solid rgba(201,146,42,0.15)', paddingBottom: '0.5rem' }}>LATEST DISPATCHES</h3>
          
          <article className="feed-item">
            <div className="font-mono text-gold-500 mb-2" style={{ fontSize: '0.6rem', letterSpacing: '3px' }}>MARKET</div>
            <h2 style={{ fontSize: '18px', marginBottom: '0.5rem' }}>Nifty 50 Closes Higher Amid Volatility</h2>
            <p className="text-ink-300" style={{ fontSize: '14px', lineHeight: 1.6 }}>Banking stocks carried the index to a new weekly high, shrugging off weak global cues and stabilizing the portfolio's core large-cap exposure.</p>
          </article>

          <article className="feed-item">
            <div className="font-mono text-gold-500 mb-2" style={{ fontSize: '0.6rem', letterSpacing: '3px' }}>GOAL</div>
            <h2 style={{ fontSize: '18px', marginBottom: '0.5rem' }}>House Downpayment On Track</h2>
            <p className="text-ink-300" style={{ fontSize: '14px', lineHeight: 1.6 }}>You have crossed 40% of your target corpus for the house downpayment. The recent bump in interest rates for your liquid funds accelerates this slightly.</p>
            <div style={{ textAlign: 'right', marginTop: '1rem' }}>
              <a href="#" className="font-mono text-gold-500" style={{ fontSize: '0.85rem' }}>VIEW TRAJECTORY &rarr;</a>
            </div>
          </article>

          <article className="feed-item">
            <div className="font-mono text-gold-500 mb-2" style={{ fontSize: '0.6rem', letterSpacing: '3px' }}>TAX</div>
            <h2 style={{ fontSize: '18px', marginBottom: '0.5rem' }}>New Regime Benefits Crystallize</h2>
            <p className="text-ink-300" style={{ fontSize: '14px', lineHeight: 1.6 }}>A recent update in the standard deduction under the new regime makes it highly favorable for your income bracket, saving an estimated ₹12,400 over the old regime.</p>
          </article>
        </section>

        {/* CENTER COLUMN: Goals & SIP */}
        <section>
          <h3 className="font-mono text-ink-500 mb-4" style={{ fontSize: '0.9rem', letterSpacing: '2px', borderBottom: '1px solid rgba(201,146,42,0.15)', paddingBottom: '0.5rem' }}>PORTFOLIO STATUS</h3>

          {/* SIP Reminder Box */}
          <div className="mb-8" style={{ border: '1px solid var(--gold-500)', padding: '1.5rem', background: 'var(--ember-800)', borderRadius: '2px' }}>
            <div className="font-mono text-gold-500" style={{ fontSize: '0.75rem', letterSpacing: '1px', marginBottom: '0.5rem' }}>SIP DUE IN 3 DAYS</div>
            <h4 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Parag Parikh Flexi Cap Fund</h4>
            <div className="flex justify-between items-center mt-4">
              <span className="font-mono text-ink-300">₹{formatINR(monthlySip)}</span>
              <button className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>PAY NOW &rarr;</button>
            </div>
          </div>

          {/* Goals */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <h4 style={{ fontSize: '15px' }}>Retirement Corpus</h4>
              <span className="font-mono text-signal-green" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>ON TRACK</span>
            </div>
            <div style={{ height: '2px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: `${retirementPct}%`, background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500" style={{ fontSize: '0.8rem', textAlign: 'right' }}>₹{toCr(retirementCurrent)} / ₹{toCr(retirementTarget)}</div>
          </div>

          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <h4 style={{ fontSize: '15px' }}>{primaryGoal?.name || 'Primary Goal'}</h4>
              <span className="font-mono text-signal-green" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>{goalPct >= 40 ? 'ON TRACK' : 'BUILDING'}</span>
            </div>
            <div style={{ height: '2px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: `${goalPct}%`, background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500" style={{ fontSize: '0.8rem', textAlign: 'right' }}>₹{formatINR(goalCurrent)} / ₹{formatINR(primaryGoal?.target_amount || 0)}</div>
          </div>

          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <h4 style={{ fontSize: '15px' }}>Monthly Surplus</h4>
              <span className="font-mono text-signal-red" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>{monthlySurplus >= 0 ? 'HEALTHY' : 'NEGATIVE'}</span>
            </div>
            <div style={{ height: '2px', background: 'var(--ember-600)', width: '100%', marginBottom: '0.5rem' }}>
              <div style={{ height: '100%', width: `${Math.max(5, Math.min(100, Math.round(Math.abs(monthlySurplus) / 1000)))}%`, background: 'var(--gold-500)' }}></div>
            </div>
            <div className="font-mono text-ink-500" style={{ fontSize: '0.8rem', textAlign: 'right' }}>₹{formatINR(monthlySurplus)} / month</div>
          </div>
        </section>

        {/* RIGHT COLUMN: Market & Quick Actions */}
        <section>
          {/* Market Ticker */}
          <div className="mb-8 overflow-hidden" style={{ borderBottom: '1px solid rgba(201,146,42,0.15)', paddingBottom: '1.5rem' }}>
            <h3 className="font-mono text-ink-500 mb-4" style={{ fontSize: '0.9rem', letterSpacing: '2px' }}>MARKETS</h3>
            
            <div className="font-mono" style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <div className="flex justify-between">
                <span>NIFTY 50</span>
                <span className="text-signal-green">▲ 0.4%</span>
              </div>
              <div className="flex justify-between text-ink-300" style={{ fontSize: '0.8rem' }}>
                <span>22,456.20</span>
              </div>
              
              <div className="flex justify-between mt-2">
                <span>SENSEX</span>
                <span className="text-signal-green">▲ 0.3%</span>
              </div>
              <div className="flex justify-between text-ink-300" style={{ fontSize: '0.8rem' }}>
                <span>73,903.91</span>
              </div>

              <div className="flex justify-between mt-2">
                <span>GOLD (10g)</span>
                <span className="text-signal-red">▼ 0.2%</span>
              </div>
              <div className="flex justify-between text-ink-300" style={{ fontSize: '0.8rem' }}>
                <span>₹71,200</span>
              </div>
            </div>
          </div>

          <div>
             <h3 className="font-mono text-ink-500 mb-4" style={{ fontSize: '0.9rem', letterSpacing: '2px' }}>ACTIONS</h3>
             <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
               <li><a href="#" style={{ fontSize: '15px' }} className="font-display">Download Tax Statement</a></li>
               <li><a href="#" style={{ fontSize: '15px' }} className="font-display">Update Risk Profile</a></li>
               <li><a href="#" style={{ fontSize: '15px' }} className="font-display">Mandate New SIP</a></li>
             </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
