import React, { useState } from 'react';
import { 
  Building2, 
  Users, 
  AlertTriangle, 
  TrendingUp, 
  BarChart3, 
  Flame, 
  Award, 
  ShieldAlert, 
  FileSpreadsheet, 
  Download,
  CheckCircle2,
  Bell
} from 'lucide-react';

export default function TpoCommandCenter({
  overview,
  vulnerable,
  heatmap,
  alerts,
  industryDemand,
  onSelectStudent
}) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'vulnerable' | 'heatmap' | 'alerts'
  const [thresholdFilter, setThresholdFilter] = useState(60.0);

  if (!overview) {
    return (
      <div className="glass-panel" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h3 style={{ color: '#fff' }}>Loading Institutional TPO Analytics...</h3>
        <p style={{ color: 'var(--text-secondary)' }}>Aggregating batch-wide employability distributions and branch benchmarks</p>
      </div>
    );
  }

  const branchKeys = Object.keys(overview.branch_analytics || {});

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Banner & KPI Metrics */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Building2 size={24} color="#38bdf8" />
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>
                Training & Placement Officer (TPO) Institutional Command Center
              </h2>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Real-time institutional cohort intelligence, early intervention alerts, and industry alignment
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={() => alert("Exporting full cohort placement report (CSV)...")}
              className="btn-secondary" 
              style={{ fontSize: '0.8rem' }}
            >
              <Download size={14} /> Export Cohort Report
            </button>
          </div>
        </div>

        {/* 4 High-Level Metric Tiles */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL BATCH COHORT</div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#fff' }}>{overview.cohort_size}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Engineering Batch of 2026</div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>PREDICTED PLACEMENT RATE</div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#34d399' }}>
              {overview.overall_placement_rate_predicted}%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#34d399' }}>Calibrated Stacked Ensemble</div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>READY TO INTERVIEW</div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#38bdf8' }}>
              {overview.readiness_distribution?.Ready || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
              {overview.readiness_percentages?.Ready}% of total batch
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(244, 63, 94, 0.3)' }}>
            <div style={{ fontSize: '0.75rem', color: '#fb7185', fontWeight: 600 }}>VULNERABLE SEGMENT (&lt;60%)</div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#fb7185' }}>
              {overview.readiness_distribution?.['Needs Training'] || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#fb7185' }}>Requires targeted training</div>
          </div>
        </div>
      </div>

      {/* TPO Sub-Navigation */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
        {[
          { id: 'overview', label: 'Departmental Breakdown', icon: BarChart3 },
          { id: 'vulnerable', label: 'Cohort Vulnerability Filters (<60%)', icon: ShieldAlert },
          { id: 'heatmap', label: 'Institutional Skill Deficit Heatmap', icon: FileSpreadsheet },
          { id: 'alerts', label: 'Mentor Alert Center', icon: Bell },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: isActive ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                color: isActive ? '#38bdf8' : 'var(--text-secondary)',
                border: isActive ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid transparent',
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: Departmental Breakdown */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '14px' }}>
              Branch-Wise Placement Readiness Metrics
            </h3>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '10px 14px' }}>DEPARTMENT BRANCH</th>
                    <th style={{ padding: '10px 14px' }}>COHORT SIZE</th>
                    <th style={{ padding: '10px 14px' }}>PLACEMENT PROBABILITY</th>
                    <th style={{ padding: '10px 14px' }}>READY STATUS %</th>
                    <th style={{ padding: '10px 14px' }}>VULNERABILITY %</th>
                    <th style={{ padding: '10px 14px' }}>AVG CGPA</th>
                  </tr>
                </thead>
                <tbody>
                  {branchKeys.map((b) => {
                    const data = overview.branch_analytics[b];
                    return (
                      <tr key={b} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '12px 14px', fontWeight: 600, color: '#fff' }}>{b}</td>
                        <td style={{ padding: '12px 14px', color: 'var(--text-secondary)' }}>{data.total}</td>
                        <td style={{ padding: '12px 14px', fontWeight: 700, color: data.avg_probability >= 70 ? '#34d399' : '#fbbf24' }}>
                          {data.avg_probability}%
                        </td>
                        <td style={{ padding: '12px 14px' }}>
                          <span className="badge badge-ready">{data.readiness_pct}%</span>
                        </td>
                        <td style={{ padding: '12px 14px' }}>
                          <span className={data.vulnerable_pct > 25 ? 'badge badge-training' : 'badge badge-near-ready'}>
                            {data.vulnerable_pct}%
                          </span>
                        </td>
                        <td style={{ padding: '12px 14px', color: '#e2e8f0' }}>{data.avg_cgpa}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Industry Demand Overview */}
          {industryDemand && (
            <div className="glass-panel" style={{ padding: '20px' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '6px' }}>
                Corporate Campus Hiring Skill Demand (from Official Postings)
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
                Curricula alignment recommendations derived from live corporate opening requirements
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px' }}>
                {industryDemand.map((d) => (
                  <div key={d.skill} style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                      <span style={{ color: '#fff', fontWeight: 600 }}>{d.skill}</span>
                      <span style={{ color: '#38bdf8', fontWeight: 700 }}>{d.demand_count} roles</span>
                    </div>
                    <div style={{ width: '100%', height: '4px', background: '#334155', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ width: `${d.share_pct}%`, height: '100%', background: '#38bdf8' }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Cohort Vulnerability Filter */}
      {activeTab === 'vulnerable' && vulnerable && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                  Vulnerable Cohort Drill-Down (&lt;60% Employability Probability)
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Total Flagged: <strong style={{ color: '#fb7185' }}>{vulnerable.count} students</strong> requiring departmental intervention
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Threshold:</span>
                <select
                  value={thresholdFilter}
                  onChange={(e) => setThresholdFilter(Number(e.target.value))}
                  style={{
                    background: 'rgba(30, 41, 59, 0.8)',
                    color: '#fff',
                    border: '1px solid var(--border-subtle)',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '0.8rem'
                  }}
                >
                  <option value={50}>Critical (&lt;50%)</option>
                  <option value={60}>Standard (&lt;60%)</option>
                  <option value={65}>Elevated (&lt;65%)</option>
                </select>

                <button 
                  onClick={() => alert(`Enrolling ${vulnerable.count} students into 4-Week Placement Bootcamp!`)}
                  className="btn-primary" 
                  style={{ fontSize: '0.75rem' }}
                >
                  Schedule Department Bootcamp
                </button>
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '8px 12px' }}>STUDENT ID</th>
                    <th style={{ padding: '8px 12px' }}>BRANCH</th>
                    <th style={{ padding: '8px 12px' }}>SEM</th>
                    <th style={{ padding: '8px 12px' }}>CGPA</th>
                    <th style={{ padding: '8px 12px' }}>BACKLOGS</th>
                    <th style={{ padding: '8px 12px' }}>CODING APTITUDE</th>
                    <th style={{ padding: '8px 12px' }}>PROBABILITY</th>
                    <th style={{ padding: '8px 12px' }}>TARGET TRACK</th>
                  </tr>
                </thead>
                <tbody>
                  {vulnerable.students?.map((s) => (
                    <tr key={s.student_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '10px 12px', color: '#38bdf8', fontWeight: 600 }}>{s.student_id}</td>
                      <td style={{ padding: '10px 12px', color: '#fff' }}>{s.branch}</td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>Sem {s.semester}</td>
                      <td style={{ padding: '10px 12px', color: '#e2e8f0' }}>{s.cgpa}</td>
                      <td style={{ padding: '10px 12px', color: s.active_backlogs > 0 ? '#fb7185' : '#34d399', fontWeight: 600 }}>
                        {s.active_backlogs} active
                      </td>
                      <td style={{ padding: '10px 12px', color: '#e2e8f0' }}>{s.coding_benchmark}/100</td>
                      <td style={{ padding: '10px 12px' }}>
                        <span className="badge badge-training">{s.placement_probability}%</span>
                      </td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>{s.primary_track}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Institutional Skill Deficit Heatmap */}
      {activeTab === 'heatmap' && heatmap && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '6px' }}>
              Institutional Skill Deficit Heatmap (% of Students Lacking Proficiency)
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Visualizing widespread curriculum voids across engineering branches to guide departmental workshop allocation
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '12px 14px' }}>BRANCH</th>
                    <th style={{ padding: '12px 14px' }}>DSA</th>
                    <th style={{ padding: '12px 14px' }}>SQL</th>
                    <th style={{ padding: '12px 14px' }}>PYTHON</th>
                    <th style={{ padding: '12px 14px' }}>WEB / REACT</th>
                    <th style={{ padding: '12px 14px' }}>CLOUD / DEVOPS</th>
                    <th style={{ padding: '12px 14px' }}>AI / ML</th>
                  </tr>
                </thead>
                <tbody>
                  {heatmap.map((row) => (
                    <tr key={row.branch} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '12px 14px', fontWeight: 700, color: '#fff' }}>{row.branch}</td>
                      {['DSA', 'SQL', 'Python', 'Web/React', 'Cloud/DevOps', 'AI/ML'].map((col) => {
                        const val = row[col] || 0;
                        const bg = val > 65 ? 'rgba(244, 63, 94, 0.25)' : val > 45 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.15)';
                        const txtColor = val > 65 ? '#fb7185' : val > 45 ? '#fbbf24' : '#34d399';
                        return (
                          <td key={col} style={{ padding: '12px 14px' }}>
                            <div style={{
                              background: bg,
                              color: txtColor,
                              padding: '6px 10px',
                              borderRadius: '6px',
                              fontWeight: 700,
                              textAlign: 'center',
                              width: 'fit-content'
                            }}>
                              {val}%
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Mentor Alert Center */}
      {activeTab === 'alerts' && alerts && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '6px' }}>
              Actionable Mentor Notifications & Early Intervention Triggers
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              High-priority flags for outperforming referrals and vulnerable students
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {alerts.map((alt) => {
                const isCrit = alt.priority === 'CRITICAL';
                const isHigh = alt.priority === 'HIGH';
                return (
                  <div key={alt.id} style={{
                    background: isCrit ? 'rgba(244, 63, 94, 0.08)' : isHigh ? 'rgba(16, 185, 129, 0.08)' : 'rgba(30, 41, 59, 0.5)',
                    borderLeft: `4px solid ${isCrit ? '#f43f5e' : isHigh ? '#10b981' : '#38bdf8'}`,
                    padding: '16px',
                    borderRadius: '0 10px 10px 0',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={isCrit ? 'badge badge-training' : isHigh ? 'badge badge-ready' : 'badge badge-cyan'}>
                          {alt.type} • {alt.priority}
                        </span>
                        <strong style={{ color: '#fff' }}>{alt.student_name} ({alt.student_id})</strong>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{alt.branch}</span>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{alt.metric}</span>
                    </div>

                    <p style={{ fontSize: '0.85rem', color: '#e2e8f0' }}>{alt.message}</p>
                    <div style={{ fontSize: '0.8rem', color: '#38bdf8', marginTop: '4px' }}>
                      👉 <strong>Action Required:</strong> {alt.recommended_action}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
