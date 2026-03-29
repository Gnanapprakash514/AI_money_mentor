import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, Link } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Flame, FileText, HeartPulse, Users } from 'lucide-react';

const MENU_ITEMS = [
  { path: '/', name: 'Dashboard', icon: LayoutDashboard },
  { path: '/onboarding', name: 'Onboarding', icon: MessageSquare },
  { path: '/fire', name: 'FIRE Planner', icon: Flame },
  { path: '/tax', name: 'Tax Wizard', icon: FileText },
  { path: '/score', name: 'Health Score', icon: HeartPulse },
  { path: '/couple', name: 'Couple Planner', icon: Users },
];

export default function Layout() {
  const location = useLocation();
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  const getPageTitle = () => {
    const active = MENU_ITEMS.find(i => i.path === location.pathname);
    return active ? active.name : 'Unknown Page';
  };

  return (
    <div className="flex bg-ember-900 min-h-screen">
      {/* Sidebar */}
      <nav className="sidebar-container">
        <div style={{ height: '56px', display: 'flex', alignItems: 'center', padding: '0 1.5rem', borderBottom: '1px solid rgba(201,146,42,0.15)' }}>
          <span className="font-display" style={{ color: 'var(--gold-500)', fontSize: '1.2rem', letterSpacing: '1px' }}>INK & EMBER</span>
        </div>
        <div style={{ padding: '1.5rem 0' }}>
          {MENU_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.75rem 1.5rem',
                  color: isActive ? 'var(--ink-100)' : 'var(--ink-300)',
                  backgroundColor: isActive ? 'var(--ember-700)' : 'transparent',
                  borderLeft: isActive ? '3px solid var(--gold-500)' : '3px solid transparent',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={18} style={{ marginRight: '1rem', color: isActive ? 'var(--gold-500)' : 'inherit' }} />
                <span className="menu-label font-mono" style={{ paddingTop: '2px' }}>{item.name}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="main-content flex-col w-full">
        {/* Top bar */}
        <header className="top-bar">
          <h1 style={{ fontSize: '1.2rem', margin: 0 }}>{getPageTitle()}</h1>
          <div className="font-mono text-ink-300" style={{ fontSize: '0.8rem', letterSpacing: '0.5px' }}>
            {today.toUpperCase()}
          </div>
        </header>

        {/* Page Content */}
        <div className="page-container">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
