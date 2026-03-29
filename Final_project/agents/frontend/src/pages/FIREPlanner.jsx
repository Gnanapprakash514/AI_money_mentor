import React, { useEffect, useState, useRef } from 'react';
import { fetchFirePlan } from '../api/client';

const MOCK_NODES = [
  { age: 34, title: "The Accumulation Phase", desc: "Aggressive SIP step-up by 15% annually to capture market upside." },
  { age: 40, title: "Debt Free Horizon", desc: "Final EMI paid on the primary residence. Cashflow unlocks." },
  { age: 45, title: "Corpus Crossover", desc: "Investment returns exceed active annual salary." },
  { age: 50, title: "FIRE ACHIEVED", desc: "Target corpus of ₹8.4Cr secured. 3.5% safe withdrawal rate unlocked." }
];

export default function FIREPlanner() {
  const [data, setData] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    fetchFirePlan({}).then(res => setData(res));
  }, []);

  const handleWheel = (e) => {
    if (containerRef.current) {
      containerRef.current.scrollLeft += e.deltaY;
      // Prevent vertical if scrolling horizontally in layout
    }
  };

  return (
    <div style={{ padding: '0 1rem' }}>
      <header className="mb-8">
        <h1 style={{ fontSize: '36px', marginBottom: '0.5rem' }}>Your Timeline to Freedom</h1>
        <p className="font-mono text-ink-300" style={{ fontSize: '0.9rem', maxWidth: '800px' }}>
          Without changes, retire at 67. With this layout, retire at <span className="text-gold-500 font-bold" style={{fontSize:'1rem'}}>50</span>.
        </p>
      </header>

      {/* Timeline Rail */}
      <div 
        ref={containerRef}
        onWheel={handleWheel}
        style={{ 
          position: 'relative', 
          height: '400px', 
          width: '100%', 
          overflowX: 'auto', 
          overflowY: 'hidden', 
          display: 'flex', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(201,146,42,0.15)',
          borderTop: '1px solid rgba(201,146,42,0.15)',
          padding: '0 2rem'
        }}
      >
        {/* The Golden Line */}
        <div style={{ position: 'absolute', top: '50%', left: 0, width: '2000px', height: '1px', background: 'var(--gold-500)', zIndex: 1 }}></div>

        {/* Nodes */}
        <div style={{ display: 'flex', gap: '8rem', position: 'relative', zIndex: 2 }}>
          {MOCK_NODES.map((node, i) => {
            const isTop = i % 2 === 0;
            const isLast = i === MOCK_NODES.length - 1;
            
            return (
              <div key={i} className="flex-col items-center relative" style={{ minWidth: '200px' }}>
                {/* Node Card Container */}
                <div 
                  className="card"
                  style={{ 
                    position: 'absolute', 
                    top: isTop ? '-140px' : '40px', 
                    left: '50%', 
                    transform: 'translateX(-50%)',
                    width: '200px',
                    padding: '1.25rem',
                    textAlign: 'center'
                  }}
                >
                  <div className="font-display" style={{ fontSize: '24px', fontWeight: 'bold' }}>Age {node.age}</div>
                  <div style={{ fontSize: '14px', marginBottom: '0.5rem', fontWeight: 500 }}>{node.title}</div>
                  <div className="text-ink-300" style={{ fontSize: '12px', lineHeight: 1.4 }}>{node.desc}</div>
                </div>

                {/* The Dot */}
                <div 
                  style={{ 
                    width: isLast ? '16px' : '8px', 
                    height: isLast ? '16px' : '8px', 
                    background: 'var(--ember-900)',
                    border: isLast ? '3px solid var(--gold-500)' : '2px solid var(--gold-500)',
                    borderRadius: '50%',
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    backgroundColor: isLast ? 'var(--gold-500)' : 'var(--ember-800)'
                  }}
                ></div>

                {/* Vertical Connector Line */}
                <div style={{ 
                  width: '1px', 
                  height: '40px', 
                  background: 'var(--gold-500)', 
                  position: 'absolute',
                  top: isTop ? '-20px' : '0px',
                  opacity: 0.3
                }}></div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Data View */}
      <div className="flex mt-8 gap-4">
        <div className="w-full">
          <h3 className="font-display mb-4" style={{ fontSize: '20px', color: 'var(--ink-100)' }}>SIP Composition</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <tbody>
              {['Parag Parikh Flexi', 'Nifty 50 Index', 'Motilal Midcap', 'Liquid Fund'].map((f, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(201,146,42,0.15)' }}>
                  <td className="font-mono text-ink-300 py-2" style={{ padding: '0.75rem 0' }}>{f}</td>
                  <td className="font-mono text-right" style={{ padding: '0.75rem 0' }}>₹{25000 - i*5000}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="w-full panel" style={{ padding: '2rem' }}>
          <h3 className="font-display mb-4" style={{ fontSize: '20px', color: 'var(--ink-100)' }}>The Math</h3>
          <div className="flex justify-between mb-4">
            <span className="font-mono text-ink-300">Corpus Target</span>
            <span className="font-mono">₹8.4 Cr</span>
          </div>
          <div className="flex justify-between mb-4">
            <span className="font-mono text-ink-300">Current Assembled</span>
            <span className="font-mono text-gold-500">₹1.2 Cr</span>
          </div>
          <div className="flex justify-between mb-4">
            <span className="font-mono text-ink-300">Monthly Gap to Close</span>
            <span className="font-mono text-signal-red">₹35,000</span>
          </div>
        </div>
      </div>

      {data?.output && (
        <div className="panel mt-8" style={{ padding: '1rem' }}>
          <h3 className="font-display mb-3" style={{ fontSize: '18px' }}>AI FIRE Analysis</h3>
          <p className="text-ink-300" style={{ whiteSpace: 'pre-wrap' }}>{data.output}</p>
        </div>
      )}

    </div>
  );
}
