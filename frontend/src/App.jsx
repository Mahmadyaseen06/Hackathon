import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StudentDiagnostics from './components/StudentDiagnostics';
import JobIntelligenceView from './components/JobIntelligenceView';
import TpoCommandCenter from './components/TpoCommandCenter';
import StudentProfileModal from './components/StudentProfileModal';
import confetti from 'canvas-confetti';

export default function App() {
  const [activeView, setActiveView] = useState('student'); // 'student' | 'jobs' | 'tpo'
  const [personas, setPersonas] = useState([]);
  const [currentStudent, setCurrentStudent] = useState(null);
  
  // Student Module State
  const [prediction, setPrediction] = useState(null);
  const [skillGap, setSkillGap] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [resources, setResources] = useState(null);
  const [projects, setProjects] = useState(null);
  const [internships, setInternships] = useState(null);
  const [tracker, setTracker] = useState(null);
  
  // Job Intelligence State
  const [jobMatches, setJobMatches] = useState(null);

  // TPO Module State
  const [tpoOverview, setTpoOverview] = useState(null);
  const [tpoVulnerable, setTpoVulnerable] = useState(null);
  const [tpoHeatmap, setTpoHeatmap] = useState(null);
  const [tpoAlerts, setTpoAlerts] = useState(null);
  const [industryDemand, setIndustryDemand] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(true);

  // 1. Initial Load: Fetch Personas & TPO Data
  useEffect(() => {
    async function initApp() {
      try {
        const pRes = await fetch('/api/demo-students');
        if (pRes.ok) {
          const students = await pRes.json();
          setPersonas(students);
          if (students.length > 0) {
            setCurrentStudent(students[0]); // default to Priya Patel
          }
        }
        
        // Load TPO batch metrics
        loadTpoData();
      } catch (err) {
        console.warn('Backend API warming up or not yet listening:', err);
        setApiOnline(false);
      }
    }
    initApp();
  }, []);

  // 2. Fetch all predictions & upskilling modules when currentStudent changes
  useEffect(() => {
    if (!currentStudent) return;
    evaluateStudentProfile(currentStudent);
  }, [currentStudent]);

  async function evaluateStudentProfile(student) {
    setLoading(true);
    try {
      // Predict Employability & SHAP XAI
      const predRes = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(student)
      });
      const predData = await predRes.json();
      setPrediction(predData);

      if (predData.readiness_status === 'Ready') {
        confetti({ particleCount: 60, spread: 60, origin: { y: 0.7 } });
      }

      // Skill Gap Diagnostic
      const gapRes = await fetch('/api/skill-gap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(student)
      });
      const gapData = await gapRes.json();
      setSkillGap(gapData);

      // Collect missing skills
      const missingSkills = [
        ...(gapData.critical_gaps || []).map((g) => g.skill),
        ...(gapData.minor_gaps || []).map((g) => g.skill)
      ];

      // Personalized Roadmap
      const roadRes = await fetch('/api/roadmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student,
          missing_skills: missingSkills,
          target_role: student.target_role || 'Full-Stack Developer',
          target_lpa: student.target_lpa || 12.0
        })
      });
      setRoadmap(await roadRes.json());

      // Curated YouTube & NPTEL Resources
      const resRes = await fetch('/api/resources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ missing_skills: missingSkills })
      });
      setResources(await resRes.json());

      // Project Ladder
      const projRes = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: student.skills, missing_skills: missingSkills })
      });
      setProjects(await projRes.json());

      // Internships
      const internRes = await fetch('/api/internships', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(student)
      });
      setInternships(await internRes.json());

      // Daily Tracker
      const trackRes = await fetch(`/api/tracker/${student.student_id}?github=${student.github_username || ''}&leetcode=${student.leetcode_username || ''}`);
      setTracker(await trackRes.json());

      // Job Intelligence Match
      const jobRes = await fetch('/api/jobs/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...student, placement_probability: predData.placement_probability })
      });
      setJobMatches(await jobRes.json());

      setApiOnline(true);
    } catch (err) {
      console.error('Error evaluating student:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadTpoData() {
    try {
      const [ov, vul, hm, alt, dem] = await Promise.all([
        fetch('/api/tpo/overview').then((r) => r.json()),
        fetch('/api/tpo/vulnerable').then((r) => r.json()),
        fetch('/api/tpo/skill-heatmap').then((r) => r.json()),
        fetch('/api/tpo/alerts').then((r) => r.json()),
        fetch('/api/tpo/industry-demand').then((r) => r.json()),
      ]);
      setTpoOverview(ov);
      setTpoVulnerable(vul);
      setTpoHeatmap(hm);
      setTpoAlerts(alt);
      setIndustryDemand(dem);
    } catch (e) {
      console.warn('TPO data loading error:', e);
    }
  }

  async function handleLogActivity(activityPayload) {
    try {
      await fetch('/api/tracker/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(activityPayload)
      });
      // Refresh tracker
      const trackRes = await fetch(`/api/tracker/${currentStudent.student_id}`);
      setTracker(await trackRes.json());
    } catch (e) {
      console.error('Log activity error:', e);
    }
  }

  async function handleRefreshJobs() {
    try {
      await fetch('/api/jobs/refresh', { method: 'POST' });
      // Re-evaluate current matches
      if (currentStudent) {
        const jobRes = await fetch('/api/jobs/match', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentStudent)
        });
        setJobMatches(await jobRes.json());
      }
      alert('Background refresh across official company feeds triggered!');
    } catch (e) {
      console.error('Job refresh error:', e);
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        activeView={activeView}
        setActiveView={setActiveView}
        personas={personas}
        activePersona={currentStudent}
        onSelectPersona={(p) => setCurrentStudent(p)}
        onOpenCustomModal={() => setIsModalOpen(true)}
        apiOnline={apiOnline}
      />

      <main style={{ maxWidth: '1440px', width: '100%', margin: '0 auto', padding: '24px 20px', flex: 1 }}>
        {activeView === 'student' && (
          <StudentDiagnostics
            student={currentStudent || {}}
            prediction={prediction}
            skillGap={skillGap}
            roadmap={roadmap}
            resources={resources}
            projects={projects}
            internships={internships}
            tracker={tracker}
            onLogActivity={handleLogActivity}
            loading={loading}
          />
        )}

        {activeView === 'jobs' && (
          <JobIntelligenceView
            jobMatches={jobMatches}
            student={currentStudent || {}}
            onRefreshJobs={handleRefreshJobs}
          />
        )}

        {activeView === 'tpo' && (
          <TpoCommandCenter
            overview={tpoOverview}
            vulnerable={tpoVulnerable}
            heatmap={tpoHeatmap}
            alerts={tpoAlerts}
            industryDemand={industryDemand}
            onSelectStudent={(s) => {
              setCurrentStudent(s);
              setActiveView('student');
            }}
          />
        )}
      </main>

      {/* Custom Profile Modal */}
      <StudentProfileModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        currentStudent={currentStudent}
        onSave={(updated) => {
          setCurrentStudent(updated);
        }}
      />
    </div>
  );
}
