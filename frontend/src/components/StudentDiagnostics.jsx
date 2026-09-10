import { 
  Sparkles, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Compass, 
  BookOpen, 
  Video, 
  GraduationCap, 
  Code2, 
  Rocket, 
  Flame, 
  Calendar, 
  Clock, 
  ExternalLink,
  ChevronRight,
  Layers,
  Award,
  BarChart3
} from 'lucide-react';

export default function StudentDiagnostics({
  student,
  prediction,
  skillGap,
  roadmap,
  resources,
  projects,
  internships,
  tracker,
  onLogActivity,
  loading
}) {
  const [activeTab, setActiveTab] = useState('xai'); // 'xai' | 'roadmap' | 'resources' | 'tracker'
  const [logDetails, setLogDetails] = useState('');
  const [logType, setLogType] = useState('dsa_solved');
  const [logDuration, setLogDuration] = useState(60);

  if (loading || !prediction) {
    return (
      <div style={{ padding: '60px 20px', textAlign: 'center' }}>
        <div className="animate-glow" style={{ fontSize: '2rem', marginBottom: '12px' }}>⚡</div>
        <h3 style={{ color: '#fff' }}>Running ML Employability & SHAP Factor Inference...</h3>
        <p style={{ color: 'var(--text-secondary)' }}>Evaluating multi-dimensional parameters across institutional benchmarks</p>
      </div>
    );
  }

  const prob = prediction.placement_probability ?? 50.0;
  const readiness = prediction.readiness_status ?? 'Needs Training';
  
  const getBadgeClass = (r) => {
    if (r === 'Ready') return 'badge-ready';
    if (r === 'Near-Ready') return 'badge-near-ready';
    return 'badge-training';
  };

  const handleActivitySubmit = (e) => {
    e.preventDefault();
    if (!logDetails.trim()) return;
    onLogActivity({
      student_id: student.student_id,
      activity_type: logType,
      details: logDetails,
      duration_minutes: Number(logDuration)
    });
    setLogDetails('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner: Student Identity & High-Level Prediction Gauge */}
      <div className="glass-panel" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute',
          top: '-50px',
          right: '-50px',
          width: '200px',
          height: '200px',
          background: prob >= 75 ? 'rgba(16, 185, 129, 0.1)' : prob >= 60 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(244, 63, 94, 0.1)',
          borderRadius: '50%',
          filter: 'blur(50px)',
          pointerEvents: 'none'
        }} />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>
                {student.name}
              </h2>
              <span className={`badge ${getBadgeClass(readiness)}`} style={{ fontSize: '0.8rem', padding: '4px 12px' }}>
                {readiness}
              </span>
              <span className="badge badge-cyan" style={{ fontSize: '0.75rem' }}>
                {student.branch} • Sem {student.semester}
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Target Role: <strong style={{ color: '#fff' }}>{student.target_role || 'Full-Stack Developer'}</strong> • 
              Target Package: <strong style={{ color: '#38bdf8' }}>₹{student.target_lpa || 12} LPA</strong> • 
              CGPA: <strong style={{ color: '#fff' }}>{student.cgpa}</strong> • 
              Active Backlogs: <strong style={{ color: student.active_backlogs > 0 ? '#f43f5e' : '#34d399' }}>{student.active_backlogs || 0}</strong>
            </p>
          </div>

          {/* Probability Metric Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            background: 'rgba(30, 41, 59, 0.6)',
            padding: '16px 24px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)'
          }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Employability DNA Score
              </div>
              <div style={{
                fontSize: '2.25rem',
                fontWeight: 900,
                color: prob >= 75 ? '#34d399' : prob >= 60 ? '#fbbf24' : '#fb7185',
                lineHeight: 1
              }}>
                {prob}%
              </div>
            </div>
            
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '50%',
              border: `4px solid ${prob >= 75 ? '#10b981' : prob >= 60 ? '#f59e0b' : '#f43f5e'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.85rem',
              fontWeight: 800,
              color: '#fff'
            }}>
              {readiness === 'Ready' ? '✓' : readiness === 'Near-Ready' ? '⚡' : '!'}
            </div>
          </div>
        </div>

        {/* Career Track Alignment Spectrum */}
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              INSTITUTIONAL CAREER TRACK ALIGNMENT
            </span>
            <span style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
              Primary Match: <strong>{prediction.primary_recommended_track}</strong>
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
            {prediction.career_track_alignments?.map((track) => (
              <div key={track.track} style={{
                background: 'rgba(15, 23, 42, 0.6)',
                padding: '8px 12px',
                borderRadius: '8px',
                border: track.track === prediction.primary_recommended_track ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid var(--border-subtle)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
                  <span style={{ color: '#fff', fontWeight: 500 }}>{track.track}</span>
                  <span style={{ color: '#38bdf8', fontWeight: 700 }}>{track.match_pct}%</span>
                </div>
                <div style={{ width: '100%', height: '4px', background: '#334155', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${track.match_pct}%`,
                    height: '100%',
                    background: track.track === prediction.primary_recommended_track ? 'linear-gradient(90deg, #38bdf8, #818cf8)' : '#64748b'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sub-Navigation Tabs within Student Diagnostics */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
        {[
          { id: 'xai', label: 'Explainable AI (SHAP)', icon: Sparkles },
          { id: 'roadmap', label: 'Personalized Roadmap', icon: Compass },
          { id: 'resources', label: 'Curated Learning & Internships', icon: BookOpen },
          { id: 'tracker', label: 'Daily Activity & Consistency', icon: Flame },
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

      {/* TAB 1: Explainable AI (SHAP) Factor Transparency */}
      {activeTab === 'xai' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Factor Transparency Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            
            {/* Positive Contributors */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <CheckCircle2 size={18} color="#34d399" />
                <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                  Top Positive Contributors (Score Boosters)
                </h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {prediction.factor_transparency?.positive_factors?.map((f, i) => (
                  <div key={i} style={{
                    background: 'rgba(16, 185, 129, 0.08)',
                    borderLeft: '3px solid #10b981',
                    padding: '10px 14px',
                    borderRadius: '0 8px 8px 0',
                    fontSize: '0.85rem',
                    color: '#e2e8f0'
                  }}>
                    <strong style={{ color: '#34d399', marginRight: '6px' }}>
                      +{Math.abs(f.impact_pct)}%
                    </strong>
                    {f.text.replace(/^[+-][0-9.]+% due to /, '')}
                  </div>
                ))}
              </div>
            </div>

            {/* Negative Contributors / Penalizers */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <AlertTriangle size={18} color="#fb7185" />
                <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                  Top Vulnerability Penalizers (Actionable Gaps)
                </h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {prediction.factor_transparency?.negative_factors?.map((f, i) => (
                  <div key={i} style={{
                    background: 'rgba(244, 63, 94, 0.08)',
                    borderLeft: '3px solid #f43f5e',
                    padding: '10px 14px',
                    borderRadius: '0 8px 8px 0',
                    fontSize: '0.85rem',
                    color: '#e2e8f0'
                  }}>
                    <strong style={{ color: '#fb7185', marginRight: '6px' }}>
                      -{Math.abs(f.impact_pct)}%
                    </strong>
                    {f.text.replace(/^[+-][0-9.]+% due to /, '')}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* SHAP Waterfall Impact Distribution */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                  SHAP Waterfall Feature Attribution Breakdown
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Mathematical decomposition of how profile signals shift base probability to final prediction
                </p>
              </div>
              <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
                TreeExplainer Calibrated
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {prediction.factor_transparency?.waterfall?.map((item, idx) => {
                const isPos = item.impact >= 0;
                const widthPct = Math.min(100, Math.abs(item.impact) * 2.8);
                return (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.8rem' }}>
                    <span style={{ width: '170px', color: '#cbd5e1', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {item.name}
                    </span>
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', height: '22px', position: 'relative' }}>
                      <div style={{ width: '50%', display: 'flex', justifyContent: 'flex-end', paddingRight: '4px' }}>
                        {!isPos && (
                          <div style={{
                            width: `${widthPct}%`,
                            height: '14px',
                            background: 'linear-gradient(270deg, #f43f5e, #be123c)',
                            borderRadius: '3px'
                          }} />
                        )}
                      </div>
                      <div style={{ width: '2px', height: '22px', background: '#64748b' }} />
                      <div style={{ width: '50%', display: 'flex', justifyContent: 'flex-start', paddingLeft: '4px' }}>
                        {isPos && (
                          <div style={{
                            width: `${widthPct}%`,
                            height: '14px',
                            background: 'linear-gradient(90deg, #10b981, #059669)',
                            borderRadius: '3px'
                          }} />
                        )}
                      </div>
                    </div>
                    <span style={{ width: '65px', textAlign: 'right', fontWeight: 700, color: isPos ? '#34d399' : '#fb7185' }}>
                      {isPos ? `+${item.impact}%` : `${item.impact}%`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Skill Gap Benchmark Diagnostic */}
          {skillGap && (
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                    Target Track Competency Diagnostic: {skillGap.track_title}
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Benchmark alignment: {skillGap.target_lpa_range}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TRACK FIT</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#38bdf8' }}>
                    {skillGap.track_readiness_score}%
                  </div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                {/* Critical Gaps */}
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px', borderRadius: '8px' }}>
                  <div style={{ color: '#fb7185', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AlertTriangle size={14} /> Critical Deficits (Urgent Focus)
                  </div>
                  {skillGap.critical_gaps?.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {skillGap.critical_gaps.map((g) => (
                        <span key={g.skill} className="badge badge-training" style={{ fontSize: '0.75rem' }}>
                          {g.skill} (Deficit: {g.deficit})
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No critical deficits in required skills!</p>
                  )}
                </div>

                {/* Mastered Skills */}
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px', borderRadius: '8px' }}>
                  <div style={{ color: '#34d399', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={14} /> Mastered Competencies
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {skillGap.mastered_skills?.map((s) => (
                      <span key={s.skill} className="badge badge-ready" style={{ fontSize: '0.75rem' }}>
                        ✓ {s.skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Dynamic Personalized Roadmap */}
      {activeTab === 'roadmap' && roadmap && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <span className="badge badge-purple" style={{ marginBottom: '6px' }}>
                  {roadmap.tier_info?.tier_name}
                </span>
                <h3 style={{ fontSize: '1.25rem', color: '#fff', fontWeight: 800 }}>
                  Personalized 8-Week Upskilling Roadmap ({student.target_role})
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Targeting: <strong>₹{student.target_lpa || 12} LPA</strong> • Est. Total Commitment: <strong>{roadmap.estimated_hours} Hours</strong>
                </p>
              </div>
            </div>

            {/* Week-by-Week Accordion / Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {roadmap.weeks?.map((w) => (
                <div key={w.week} style={{
                  background: 'rgba(30, 41, 59, 0.5)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{
                        background: 'linear-gradient(135deg, #0284c7, #6366f1)',
                        color: '#fff',
                        fontWeight: 800,
                        fontSize: '0.75rem',
                        padding: '4px 10px',
                        borderRadius: '6px'
                      }}>
                        WEEK {w.week}
                      </span>
                      <h4 style={{ color: '#fff', fontSize: '0.95rem' }}>{w.title}</h4>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      ⏱ {w.time_estimate}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{w.focus}</p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
                    {w.actions?.map((act, idx) => (
                      <div key={idx} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ color: '#38bdf8' }}>•</span> {act}
                      </div>
                    ))}
                  </div>

                  <div style={{
                    marginTop: '8px',
                    padding: '8px 12px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    borderLeft: '3px solid #10b981',
                    borderRadius: '0 6px 6px 0',
                    fontSize: '0.75rem',
                    color: '#34d399',
                    fontWeight: 600
                  }}>
                    🎯 Checkpoint Milestone: {w.milestone}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Curated Educational Resources, Projects & Internships */}
      {activeTab === 'resources' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* YouTube Video Tutorials */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <Video size={20} color="#f43f5e" />
              <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                Curated YouTube Tutorials (Diagnosed Deficit Mapping)
              </h3>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
              {resources?.youtube_videos?.map((yt, i) => (
                <div key={i} className="glass-panel-interactive" style={{
                  background: 'rgba(30, 41, 59, 0.6)',
                  borderRadius: '10px',
                  padding: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '8px'
                }}>
                  <div>
                    <span className="badge badge-cyan" style={{ fontSize: '0.65rem', marginBottom: '6px' }}>
                      {yt.mapped_skill}
                    </span>
                    <h4 style={{ fontSize: '0.9rem', color: '#fff', lineHeight: 1.4 }}>{yt.title}</h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Channel: {yt.channel} • {yt.duration}</p>
                  </div>
                  <a
                    href={yt.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary"
                    style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.75rem', width: 'fit-content' }}
                  >
                    Watch Tutorial <ExternalLink size={12} />
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* NPTEL / SWAYAM IIT Courses */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <GraduationCap size={20} color="#818cf8" />
              <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                NPTEL & SWAYAM IIT Courses (Institutional Certification)
              </h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
              {resources?.nptel_courses?.map((c, i) => (
                <div key={i} className="glass-panel-interactive" style={{
                  background: 'rgba(30, 41, 59, 0.6)',
                  borderRadius: '10px',
                  padding: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '8px'
                }}>
                  <div>
                    <span className="badge badge-purple" style={{ fontSize: '0.65rem', marginBottom: '6px' }}>
                      {c.institution}
                    </span>
                    <h4 style={{ fontSize: '0.9rem', color: '#fff' }}>{c.name}</h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Instructor: {c.instructor} • {c.duration_weeks} Weeks</p>
                    <p style={{ fontSize: '0.75rem', color: '#38bdf8', marginTop: '4px' }}>{c.impact}</p>
                  </div>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary"
                    style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.75rem', width: 'fit-content' }}
                  >
                    Enroll on SWAYAM <ExternalLink size={12} />
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* Progressive Project Ladder */}
          {projects && (
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Code2 size={20} color="#38bdf8" />
                  <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                    Progressive Project Ladder: {projects.tier_name}
                  </h3>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {projects.description}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                {projects.projects?.map((p, i) => (
                  <div key={i} style={{
                    background: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '10px',
                    padding: '14px',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <h4 style={{ color: '#fff', fontSize: '0.9rem' }}>{p.name}</h4>
                      <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>{p.duration}</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      {p.deliverable}
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {p.concepts?.map((c, idx) => (
                        <span key={idx} style={{
                          fontSize: '0.65rem',
                          background: 'rgba(255,255,255,0.06)',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          color: '#cbd5e1'
                        }}>
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Curated Internship Programs */}
          {internships && (
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <Rocket size={20} color="#10b981" />
                <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700 }}>
                  Curated Open-Source & Research Internships (GSoC, ISRO, SIH)
                </h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
                {internships.map((prog) => (
                  <div key={prog.id} className="glass-panel-interactive" style={{
                    background: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '10px',
                    padding: '14px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '8px'
                  }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <span className="badge badge-ready" style={{ fontSize: '0.65rem' }}>
                          {prog.match_percentage}% Profile Alignment
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{prog.organization}</span>
                      </div>
                      <h4 style={{ fontSize: '0.95rem', color: '#fff', marginBottom: '4px' }}>{prog.name}</h4>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{prog.description}</p>
                      <p style={{ fontSize: '0.75rem', color: '#38bdf8', marginTop: '4px' }}>📅 {prog.timeline}</p>
                      <p style={{ fontSize: '0.75rem', color: '#34d399' }}>💰 {prog.stipend}</p>
                    </div>

                    <a
                      href={prog.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary"
                      style={{ textDecoration: 'none', padding: '6px 14px', fontSize: '0.75rem', width: 'fit-content' }}
                    >
                      Official Application Portal <ExternalLink size={12} />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Daily Monitoring & Learning Consistency Tracker */}
      {activeTab === 'tracker' && tracker && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Consistency Metrics Banner */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            <div className="glass-panel" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>30-DAY CONSISTENCY SCORE</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: tracker.consistency_score_30d >= 60 ? '#34d399' : '#fbbf24' }}>
                {tracker.consistency_score_30d}%
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Active on {tracker.active_days_30d} of the last 30 days</p>
            </div>

            <div className="glass-panel" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CUMULATIVE HOURS (30D)</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38bdf8' }}>
                {tracker.total_hours_logged_30d} hrs
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Structured practice & projects</p>
            </div>

            <div className="glass-panel" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>GITHUB CODING STREAK</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#a855f7' }}>
                {tracker.coding_profiles?.github?.current_streak} days 🔥
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>@{tracker.coding_profiles?.github?.username}</p>
            </div>

            <div className="glass-panel" style={{ padding: '16px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>LEETCODE SOLVED</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10b981' }}>
                {tracker.coding_profiles?.leetcode?.total_solved}
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{tracker.coding_profiles?.leetcode?.global_ranking}</p>
            </div>
          </div>

          {/* Activity Logger Form & History */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Form */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '12px' }}>
                Log Today's Learning Activity
              </h3>
              <form onSubmit={handleActivitySubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                    Activity Type
                  </label>
                  <select
                    value={logType}
                    onChange={(e) => setLogType(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'rgba(30, 41, 59, 0.8)',
                      color: '#fff',
                      border: '1px solid var(--border-subtle)',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '0.85rem'
                    }}
                  >
                    <option value="dsa_solved">LeetCode / DSA Problem Solved</option>
                    <option value="project_commit">Project Code Committed to GitHub</option>
                    <option value="course_completed">Course Lecture / Certification</option>
                    <option value="video_watched">Technical Video / System Design Study</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                    Details / Problem Link
                  </label>
                  <input
                    type="text"
                    value={logDetails}
                    onChange={(e) => setLogDetails(e.target.value)}
                    placeholder="e.g. Solved 3 LeetCode Mediums on Dynamic Programming"
                    style={{
                      width: '100%',
                      background: 'rgba(30, 41, 59, 0.8)',
                      color: '#fff',
                      border: '1px solid var(--border-subtle)',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                    Duration (Minutes)
                  </label>
                  <input
                    type="number"
                    value={logDuration}
                    onChange={(e) => setLogDuration(e.target.value)}
                    min="15"
                    max="360"
                    step="15"
                    style={{
                      width: '100%',
                      background: 'rgba(30, 41, 59, 0.8)',
                      color: '#fff',
                      border: '1px solid var(--border-subtle)',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>

                <button type="submit" className="btn-primary" style={{ marginTop: '8px' }}>
                  Log Activity & Update Consistency
                </button>
              </form>
            </div>

            {/* History List */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff', fontWeight: 700, marginBottom: '12px' }}>
                Recent Activity Log (Timeline)
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto' }}>
                {tracker.recent_activities?.map((item, idx) => (
                  <div key={idx} style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                    border: '1px solid var(--border-subtle)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                      <span>{item.date}</span>
                      <span>{item.duration_minutes} mins</span>
                    </div>
                    <div style={{ color: '#fff', marginTop: '2px', fontWeight: 500 }}>{item.details}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
