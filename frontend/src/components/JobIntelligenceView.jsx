import React, { useState } from 'react';
import { 
  Building2, 
  ExternalLink, 
  Filter, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  Sparkles, 
  Search, 
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  MapPin,
  Briefcase
} from 'lucide-react';

export default function JobIntelligenceView({ jobMatches, student, onRefreshJobs }) {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [minFit, setMinFit] = useState(40);
  const [onlyEligible, setOnlyEligible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedJobId, setExpandedJobId] = useState(null);

  if (!jobMatches || !jobMatches.items) {
    return (
      <div className="glass-panel" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h3 style={{ color: '#fff' }}>Loading Official Company Matches...</h3>
        <p style={{ color: 'var(--text-secondary)' }}>Matching evaluated student competencies against active company openings</p>
      </div>
    );
  }

  const companies = Array.from(new Set(jobMatches.items.map((j) => j.company))).sort();

  const filteredJobs = jobMatches.items.filter((j) => {
    if (selectedCompany && j.company !== selectedCompany) return false;
    if (j.job_fit_score < minFit) return false;
    if (onlyEligible && j.eligibility.status === 'not_eligible') return false;
    if (selectedCategory !== 'ALL' && j.category !== selectedCategory) return false;
    return true;
  });

  const getSourceBadge = (status) => {
    if (status === 'LIVE_VERIFIED') {
      return <span className="badge badge-ready" style={{ fontSize: '0.65rem' }}>🟢 LIVE VERIFIED</span>;
    }
    if (status === 'CACHED_VERIFIED') {
      return <span className="badge badge-near-ready" style={{ fontSize: '0.65rem' }}>🟡 CACHED VERIFIED</span>;
    }
    if (status === 'DEMO_DATA') {
      return <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>⚪ DEMO BENCHMARK</span>;
    }
    return <span className="badge badge-training" style={{ fontSize: '0.65rem' }}>🔴 UNAVAILABLE</span>;
  };

  const getCategoryBadge = (cat) => {
    if (cat === 'BEST_MATCH') return <span className="badge badge-ready">Best Match</span>;
    if (cat === 'NEAR_MATCH') return <span className="badge badge-near-ready">Near Match</span>;
    return <span className="badge badge-purple">Stretch Opportunity</span>;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Banner & Next Best Skill Insight */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
              Official Company Job Intelligence & Alignment
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Evaluating <strong style={{ color: '#fff' }}>{student.name}</strong> against verified openings from Google, NVIDIA, Microsoft, Amazon, Infosys, TCS, and more.
            </p>
          </div>
          <button onClick={onRefreshJobs} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
            🔄 Sync ATS Connectors
          </button>
        </div>

        {/* Most Valuable Next Skill Callout */}
        {jobMatches.insights?.most_valuable_next_skill && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: '10px',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Sparkles size={22} color="#38bdf8" />
            <div>
              <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>
                Highest ROI Next Upskilling Action
              </div>
              <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>
                Target <strong style={{ color: '#38bdf8' }}>{jobMatches.insights.most_valuable_next_skill}</strong>: {jobMatches.insights.most_valuable_reason}
              </div>
            </div>
          </div>
        )}

        {/* Summary Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px', marginTop: '16px' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>TOTAL EVALUATED</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>{jobMatches.summary?.total || 0}</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.7rem', color: '#34d399' }}>BEST MATCHES</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#34d399' }}>{jobMatches.summary?.best || 0}</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.7rem', color: '#fbbf24' }}>NEAR MATCHES</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fbbf24' }}>{jobMatches.summary?.near || 0}</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '10px 14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.7rem', color: '#c084fc' }}>STRETCH OPPORTUNITIES</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#c084fc' }}>{jobMatches.summary?.stretch || 0}</div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>FILTERS:</span>
        </div>

        {/* Company select */}
        <div>
          <select
            value={selectedCompany}
            onChange={(e) => setSelectedCompany(e.target.value)}
            style={{
              background: 'rgba(30, 41, 59, 0.8)',
              color: '#fff',
              border: '1px solid var(--border-subtle)',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem'
            }}
          >
            <option value="">All Companies ({companies.length})</option>
            {companies.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Category select */}
        <div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{
              background: 'rgba(30, 41, 59, 0.8)',
              color: '#fff',
              border: '1px solid var(--border-subtle)',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem'
            }}
          >
            <option value="ALL">All Match Categories</option>
            <option value="BEST_MATCH">Best Matches Only</option>
            <option value="NEAR_MATCH">Near Matches Only</option>
            <option value="STRETCH_OPPORTUNITY">Stretch Opportunities Only</option>
          </select>
        </div>

        {/* Min Fit Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Min Fit: <strong style={{ color: '#38bdf8' }}>{minFit}%</strong>
          </span>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={minFit}
            onChange={(e) => setMinFit(Number(e.target.value))}
            style={{ width: '100px', accentColor: '#38bdf8' }}
          />
        </div>

        {/* Only Eligible checkbox */}
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={onlyEligible}
            onChange={(e) => setOnlyEligible(e.target.checked)}
            style={{ accentColor: '#10b981' }}
          />
          Only Hard Eligible Roles
        </label>
      </div>

      {/* Job Matches List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {filteredJobs.length === 0 ? (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
            <p style={{ color: 'var(--text-secondary)' }}>No jobs match current filter criteria. Try lowering the minimum fit slider.</p>
          </div>
        ) : (
          filteredJobs.map((job) => {
            const isExpanded = expandedJobId === job.job_id;
            return (
              <div key={job.job_id} className="glass-panel" style={{ padding: '20px', transition: 'all 0.2s ease' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px' }}>
                  
                  {/* Left: Info */}
                  <div style={{ flex: 1, minWidth: '280px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>
                        {job.company}
                      </span>
                      <span style={{ color: 'var(--text-muted)' }}>•</span>
                      <span style={{ fontSize: '1rem', color: '#e2e8f0', fontWeight: 600 }}>
                        {job.title}
                      </span>
                      {getSourceBadge(job.source_status)}
                      {getCategoryBadge(job.category)}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <MapPin size={13} /> {job.location || 'India'}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Briefcase size={13} /> {job.employment_type} • {job.work_mode}
                      </span>
                    </div>

                    {/* Matched vs Missing Skills */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {job.matched_skills?.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', fontSize: '0.75rem' }}>
                          <span style={{ color: '#34d399', fontWeight: 600 }}>MATCHED:</span>
                          {job.matched_skills.map((s) => (
                            <span key={s} className="badge badge-ready" style={{ fontSize: '0.65rem' }}>✓ {s}</span>
                          ))}
                        </div>
                      )}

                      {job.missing_required_skills?.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', fontSize: '0.75rem' }}>
                          <span style={{ color: '#fb7185', fontWeight: 600 }}>MISSING CRITICAL:</span>
                          {job.missing_required_skills.map((s) => (
                            <span key={s} className="badge badge-training" style={{ fontSize: '0.65rem' }}>! {s}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right: Scores & Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    {/* Job Fit Score */}
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>7-FACTOR JOB FIT</div>
                      <div style={{
                        fontSize: '1.75rem',
                        fontWeight: 900,
                        color: job.job_fit_score >= 75 ? '#34d399' : job.job_fit_score >= 60 ? '#fbbf24' : '#fb7185'
                      }}>
                        {job.job_fit_score}%
                      </div>
                      <div style={{ fontSize: '0.7rem', color: job.eligibility.status === 'eligible' ? '#34d399' : '#fb7185' }}>
                        {job.eligibility.status === 'eligible' ? '✓ Eligible' : '✗ Gate Blocker'}
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <a
                        href={job.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-primary"
                        style={{ padding: '6px 12px', fontSize: '0.75rem', textDecoration: 'none' }}
                      >
                        View Official <ExternalLink size={12} />
                      </a>

                      <button
                        onClick={() => setExpandedJobId(isExpanded ? null : job.job_id)}
                        className="btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                      >
                        {isExpanded ? 'Hide Details' : 'Prep Plan'}
                        {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded Details Section: 7-Factor breakdown & Action Plan */}
                {isExpanded && (
                  <div style={{
                    marginTop: '16px',
                    paddingTop: '16px',
                    borderTop: '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}>
                    {/* 7-Factor Weight Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px', borderRadius: '6px', fontSize: '0.75rem' }}>
                        <div style={{ color: 'var(--text-muted)' }}>Required Skills (35%)</div>
                        <div style={{ fontWeight: 700, color: '#38bdf8' }}>{job.skill_match_score}%</div>
                      </div>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px', borderRadius: '6px', fontSize: '0.75rem' }}>
                        <div style={{ color: 'var(--text-muted)' }}>Role Align (20%)</div>
                        <div style={{ fontWeight: 700, color: '#818cf8' }}>{job.role_alignment_score}%</div>
                      </div>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px', borderRadius: '6px', fontSize: '0.75rem' }}>
                        <div style={{ color: 'var(--text-muted)' }}>Academic (15%)</div>
                        <div style={{ fontWeight: 700, color: '#34d399' }}>{job.academic_score}%</div>
                      </div>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px', borderRadius: '6px', fontSize: '0.75rem' }}>
                        <div style={{ color: 'var(--text-muted)' }}>Experience (10%)</div>
                        <div style={{ fontWeight: 700, color: '#fbbf24' }}>{job.experience_score}%</div>
                      </div>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px', borderRadius: '6px', fontSize: '0.75rem' }}>
                        <div style={{ color: 'var(--text-muted)' }}>Aptitude (10%)</div>
                        <div style={{ fontWeight: 700, color: '#c084fc' }}>{job.aptitude_score}%</div>
                      </div>
                    </div>

                    {/* Eligibility Analysis */}
                    <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '12px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
                        ACADEMIC & ELIGIBILITY VERIFICATION
                      </div>
                      {job.eligibility.reasons?.map((r, idx) => (
                        <div key={idx} style={{ fontSize: '0.75rem', color: '#34d399' }}>{r}</div>
                      ))}
                      {job.eligibility.blockers?.map((b, idx) => (
                        <div key={idx} style={{ fontSize: '0.75rem', color: '#fb7185' }}>{b}</div>
                      ))}
                    </div>

                    {/* Recommended Prep Actions */}
                    {job.recommended_actions?.length > 0 && (
                      <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '12px', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>
                          TARGETED PREPARATION PLAN TO UNLOCK THIS ROLE
                        </div>
                        {job.recommended_actions.map((act, idx) => (
                          <div key={idx} style={{ fontSize: '0.8rem', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ color: '#38bdf8' }}>•</span> {act}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
