import React from 'react';
import { Activity, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export function LandingView({ onGetStarted, onLogin, onSignUp }) {
  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Stage 1 Header Navbar matching User Specification */}
      <header style={{
        height: '72px',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 48px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', backgroundColor: '#2563eb', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
            <Activity size={22} />
          </div>
          <span style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>AI Medical Report Assistant</span>
        </div>

        {/* Login | Sign Up buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn-secondary" onClick={onLogin || onGetStarted}>
            Login
          </button>
          <button className="btn-primary" onClick={onSignUp || onGetStarted}>
            Sign Up
          </button>
        </div>
      </header>

      {/* Stage 1 Hero Section matching User ASCII Diagram */}
      <div style={{ flex: 1, maxWidth: '1000px', margin: '0 auto', padding: '64px 24px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.8rem', lineHeight: '1.2', color: '#0f172a', fontWeight: '700', marginBottom: '16px' }}>
          Understand Your Medical Reports
        </h1>
        <p style={{ fontSize: '1.25rem', color: '#475569', marginBottom: '28px', maxWidth: '640px' }}>
          Track your health history with AI in simple language.
        </p>

        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', padding: '8px 20px', borderRadius: '99px', color: '#2563eb', fontWeight: '600', fontSize: '0.95rem', marginBottom: '36px' }}>
          <span>Upload</span> → <span>Analyze</span> → <span>Understand</span> → <span>Track</span>
        </div>

        <button className="btn-primary" style={{ padding: '14px 40px', fontSize: '1.1rem', marginBottom: '48px' }} onClick={onGetStarted}>
          Get Started <ArrowRight size={20} />
        </button>

        {/* Features Bullet List */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', width: '100%', marginBottom: '48px', textAlign: 'left' }}>
          <div className="card" style={{ padding: '20px' }}>
            <CheckCircle2 color="#2563eb" size={22} style={{ marginBottom: '8px' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '600', color: '#0f172a' }}>Report Explanation</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>Clear patient-friendly explanations for medical jargon and lab values.</p>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <CheckCircle2 color="#2563eb" size={22} style={{ marginBottom: '8px' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '600', color: '#0f172a' }}>Abnormality Detection</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>Automatic flag of high/low abnormal lab values against reference bounds.</p>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <CheckCircle2 color="#2563eb" size={22} style={{ marginBottom: '8px' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '600', color: '#0f172a' }}>Historical Comparison</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>Track changes from previous reports (improving, persistent, resolved).</p>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <CheckCircle2 color="#2563eb" size={22} style={{ marginBottom: '8px' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '600', color: '#0f172a' }}>Patient-Wise Health Records</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>Isolated contexts for family members under a single user account.</p>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <CheckCircle2 color="#2563eb" size={22} style={{ marginBottom: '8px' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '600', color: '#0f172a' }}>AI Chat (RAG Powered)</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>Ask questions about your health history with strict data isolation.</p>
          </div>
        </div>

        {/* Important Message Disclaimer matching Stage 1 */}
        <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fdba74', borderRadius: '14px', padding: '24px', textAlign: 'left', width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#c2410c', fontWeight: '700', fontSize: '0.95rem', marginBottom: '8px' }}>
            <AlertCircle size={18} />
            <span>Important Disclaimer</span>
          </div>
          <p style={{ fontSize: '0.88rem', color: '#9a3412', lineHeight: '1.5' }}>
            The system is <strong>not replacing a doctor</strong>. It helps users understand medical reports, identify abnormal values, see changes from previous reports, understand whether an earlier abnormality improved or persisted, ask questions about their reports, and keep organized patient health records.
          </p>
        </div>
      </div>
    </div>
  );
}

export default LandingView;
