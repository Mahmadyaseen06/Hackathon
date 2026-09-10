import React from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Briefcase, 
  Building2, 
  UserCheck, 
  Activity, 
  Sliders, 
  RefreshCw 
} from 'lucide-react';

export default function Header({ 
  activeView, 
  setActiveView, 
  personas, 
  activePersona, 
  onSelectPersona, 
  onOpenCustomModal,
  apiOnline 
}) {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '12px 24px'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        maxWidth: '1440px',
        margin: '0 auto'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #0284c7 0%, #6366f1 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(56, 189, 248, 0.3)'
          }}>
            <GraduationCap size={24} color="#fff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
                AI Placement Predictor
              </h1>
              <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>
                v2.0 XAI
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Decode Employability DNA • Institutional Upskilling Engine
            </p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div style={{
          display: 'flex',
          background: 'rgba(30, 41, 59, 0.7)',
          padding: '4px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)'
        }}>
          <button
            onClick={() => setActiveView('student')}
            style={{
              background: activeView === 'student' ? 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)' : 'transparent',
              color: activeView === 'student' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <Activity size={16} />
            Student Diagnostics
          </button>

          <button
            onClick={() => setActiveView('jobs')}
            style={{
              background: activeView === 'jobs' ? 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)' : 'transparent',
              color: activeView === 'jobs' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <Briefcase size={16} />
            Official Job Intel
          </button>

          <button
            onClick={() => setActiveView('tpo')}
            style={{
              background: activeView === 'tpo' ? 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)' : 'transparent',
              color: activeView === 'tpo' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <Building2 size={16} />
            TPO Command Center
          </button>
        </div>

        {/* Persona Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            TEST PERSONA:
          </span>
          {personas.map((p) => {
            const isSelected = activePersona?.student_id === p.student_id;
            return (
              <button
                key={p.student_id}
                onClick={() => onSelectPersona(p)}
                style={{
                  background: isSelected ? 'rgba(56, 189, 248, 0.2)' : 'rgba(30, 41, 59, 0.6)',
                  color: isSelected ? '#38bdf8' : 'var(--text-secondary)',
                  border: isSelected ? '1px solid rgba(56, 189, 248, 0.5)' : '1px solid var(--border-subtle)',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.15s ease'
                }}
              >
                <UserCheck size={12} />
                {p.name.split(' ')[0]}
              </button>
            );
          })}
          
          <button
            onClick={onOpenCustomModal}
            className="btn-secondary"
            style={{ padding: '6px 12px', fontSize: '0.75rem' }}
            title="Edit student profile attributes"
          >
            <Sliders size={13} />
            Custom
          </button>
        </div>
      </div>
    </header>
  );
}
