import React, { useState } from 'react';
import { X, Check } from 'lucide-react';

export default function StudentProfileModal({ isOpen, onClose, currentStudent, onSave }) {
  if (!isOpen || !currentStudent) return null;

  const [formData, setFormData] = useState({
    ...currentStudent,
    skills: { ...(currentStudent.skills || {}) },
    aptitude: { ...(currentStudent.aptitude || {}) }
  });

  const handleSkillChange = (skill, val) => {
    setFormData({
      ...formData,
      skills: {
        ...formData.skills,
        [skill]: Number(val)
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 200,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '680px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '24px',
        background: '#0f172a',
        border: '1px solid rgba(56, 189, 248, 0.3)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
            Customize Student Profile Attributes
          </h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Row 1: Name, Branch, Sem */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Name</label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Branch</label>
              <select
                value={formData.branch || 'CSE'}
                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              >
                <option value="CSE">CSE</option>
                <option value="ISE">ISE</option>
                <option value="ECE">ECE</option>
                <option value="EEE">EEE</option>
                <option value="Mech">Mech</option>
                <option value="Civil">Civil</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Target Role</label>
              <select
                value={formData.target_role || 'Full-Stack Developer'}
                onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              >
                <option value="Full-Stack Developer">Full-Stack Developer</option>
                <option value="Data Analyst / ML Engineer">Data Analyst / ML Engineer</option>
                <option value="Cloud / DevOps Engineer">Cloud / DevOps Engineer</option>
                <option value="QA Specialist">QA Specialist</option>
                <option value="Core Systems / SDE">Core Systems / SDE</option>
              </select>
            </div>
          </div>

          {/* Row 2: Academics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>CGPA (0 - 10)</label>
              <input
                type="number"
                step="0.05"
                min="4"
                max="10"
                value={formData.cgpa || 7.0}
                onChange={(e) => setFormData({ ...formData, cgpa: parseFloat(e.target.value) })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Active Backlogs</label>
              <input
                type="number"
                min="0"
                max="6"
                value={formData.active_backlogs ?? 0}
                onChange={(e) => setFormData({ ...formData, active_backlogs: parseInt(e.target.value) })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Target LPA (₹)</label>
              <input
                type="number"
                step="1"
                min="3"
                max="45"
                value={formData.target_lpa || 12}
                onChange={(e) => setFormData({ ...formData, target_lpa: parseFloat(e.target.value) })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Coding Aptitude</label>
              <input
                type="number"
                min="20"
                max="100"
                value={formData.coding_benchmark || 70}
                onChange={(e) => setFormData({ ...formData, coding_benchmark: parseFloat(e.target.value) })}
                style={{ width: '100%', background: '#1e293b', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '0.85rem' }}
              />
            </div>
          </div>

          {/* Technical Skills Sliders */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8', marginBottom: '8px' }}>
              TECHNICAL PROFICIENCY RATINGS (1 - 10)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {['DSA', 'Python', 'Java', 'C++', 'SQL', 'React', 'Docker', 'Machine Learning'].map((sk) => (
                <div key={sk} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#e2e8f0', width: '100px' }}>{sk}</span>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={formData.skills[sk] || 5}
                    onChange={(e) => handleSkillChange(sk, e.target.value)}
                    style={{ flex: 1, accentColor: '#38bdf8' }}
                  />
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', width: '20px' }}>
                    {formData.skills[sk] || 5}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              <Check size={14} /> Save & Re-Evaluate DNA
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
