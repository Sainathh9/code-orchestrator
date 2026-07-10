import React, { useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useSearchParams, Navigate, useOutletContext, useParams } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { AppLayout } from '../layouts/AppLayout';
import type { AppOutletContext } from '../layouts/AppLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { useAuth } from '../hooks/useAuth';
import { executionsApi } from '../api/executions';
import { PromptInput } from '../components/PromptInput';
import { ExecutionChat } from '../components/ExecutionChat';
import { useJobPoller } from '../hooks/useJobPoller';
import type { ExecutionDetail } from '../types/execution';

// ── Icons & Banners ──────────────────────────────────────────────────────────

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M17.64 9.20455C17.64 8.56636 17.5827 7.95273 17.4764 7.36364H9V10.845H13.8436C13.635 11.97 13.0009 12.9232 12.0477 13.5614V15.8195H14.9564C16.6582 14.2527 17.64 11.9455 17.64 9.20455Z" fill="#4285F4"/>
    <path d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5614C11.2418 14.1014 10.2109 14.4205 9 14.4205C6.65591 14.4205 4.67182 12.8373 3.96409 10.71H0.957275V13.0418C2.43818 15.9832 5.48182 18 9 18Z" fill="#34A853"/>
    <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957275C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957275 13.0418L3.96409 10.71Z" fill="#FBBC05"/>
    <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="#EA4335"/>
  </svg>
);

const AppleIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M11.182 0c.087.7-.25 1.45-.697 1.97-.447.52-1.166.937-1.88.882-.1-.696.253-1.418.683-1.89C9.718.49 10.487.07 11.182 0zM13.98 11.39c-.313.91-.694 1.717-1.145 2.426-.73 1.135-1.49 2.27-2.698 2.29-1.186.02-1.565-.775-2.918-.776-1.352 0-1.77.795-2.897.795-1.186 0-2.01-1.165-2.74-2.3C.372 11.594-.43 8.82.264 6.147c.684-2.61 2.74-4.38 4.89-4.38 1.29 0 2.36.845 3.17.845.79 0 2.266-.997 3.81-.85.645.027 2.457.26 3.624 1.97-.094.06-2.158 1.26-2.135 3.753.024 2.985 2.62 3.98 2.66 3.996-.034.1-.413 1.41-.413 1.41z"/>
  </svg>
);

const AnnouncementBanner = () => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: '8px',
    background: 'rgba(107, 142, 214, 0.12)', border: '1px solid rgba(107, 142, 214, 0.2)',
    borderRadius: '8px', padding: '8px 14px', marginBottom: '24px',
  }}>
    <span style={{
      background: 'linear-gradient(135deg, #6b8ed6, #a78bfa)', color: '#fff', fontSize: '10px',
      fontWeight: 600, padding: '2px 7px', borderRadius: '4px', letterSpacing: '0.3px', textTransform: 'uppercase',
    }}>New</span>
    <span style={{ fontSize: '13px', color: '#a0a8c0' }}>LangGraph-powered self-healing is live</span>
  </div>
);

// ── Auth Pages (Unchanged visually) ──────────────────────────────────────────

const LoginPage: React.FC = () => {
  const { login, loginWithEmail, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);

  const isExpired = searchParams.get('expired') === 'true';

  useEffect(() => {
    if (isAuthenticated) navigate('/', { replace: true });
  }, [isAuthenticated, navigate]);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes('@')) {
      setEmailError('Please enter a valid email address.');
      return;
    }
    setEmailError(null);
    setSubmitting(true);
    try {
      await loginWithEmail(trimmed, password);
      navigate('/', { replace: true });
    } catch {
      setEmailError('Sign-in failed. Check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)',
    color: '#f5f0e8', padding: '12px 16px', borderRadius: '8px', fontSize: '14px', outline: 'none',
    transition: 'border-color 0.2s', fontFamily: 'var(--sans)',
  };

  const btnBase: React.CSSProperties = {
    width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
    padding: '12px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: 500, cursor: 'pointer',
    border: 'none', transition: 'all 0.18s', fontFamily: 'var(--sans)',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%', maxWidth: '340px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '48px' }}>
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
          <path d="M14 0L17.2 10.8L28 14L17.2 17.2L14 28L10.8 17.2L0 14L10.8 10.8L14 0Z" fill="#d97757"/>
        </svg>
        <span style={{ fontFamily: 'var(--serif)', fontSize: '18px', fontWeight: 600, color: '#f5f0e8', letterSpacing: '-0.2px' }}>Orchestrator</span>
      </div>
      <h1 style={{ fontFamily: 'var(--serif)', fontSize: '44px', fontWeight: 600, lineHeight: '1.15', letterSpacing: '-0.5px', color: '#f5f0e8', marginBottom: '16px' }}>
        Code fast,<br />heal faster.
      </h1>
      <p style={{ fontSize: '14px', color: '#8a8a8a', marginBottom: '28px', lineHeight: '1.6' }}>
        Build, test, and deploy production-ready code with AI-powered self-healing.
      </p>
      <AnnouncementBanner />
      {(isExpired || emailError) && (
        <div style={{ width: '100%', background: 'rgba(220, 38, 38, 0.08)', border: '1px solid rgba(220, 38, 38, 0.2)', color: '#f87171', padding: '10px 14px', borderRadius: '8px', fontSize: '13px', marginBottom: '16px', lineHeight: '1.4' }}>
          {isExpired ? 'Your session expired. Please sign in again.' : emailError}
        </div>
      )}
      <button onClick={login} disabled={submitting} style={{ ...btnBase, background: 'rgba(255,255,255,0.06)', color: '#f5f0e8', border: '1px solid rgba(255,255,255,0.10)', marginBottom: '12px' }} onMouseOver={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.10)')} onMouseOut={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}>
        <GoogleIcon /> Continue with Google
      </button>
      <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '12px', margin: '4px 0 12px' }}>
        <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.08)' }} />
        <span style={{ fontSize: '12px', color: '#555', letterSpacing: '0.3px' }}>OR</span>
        <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.08)' }} />
      </div>
      <form onSubmit={handleEmailSubmit} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <input type="email" placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)} disabled={submitting} required style={inputStyle} onFocus={e => (e.target.style.borderColor = 'rgba(255,255,255,0.28)')} onBlur={e => (e.target.style.borderColor = 'rgba(255,255,255,0.10)')} />
        <input type="password" placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} disabled={submitting} required style={inputStyle} onFocus={e => (e.target.style.borderColor = 'rgba(255,255,255,0.28)')} onBlur={e => (e.target.style.borderColor = 'rgba(255,255,255,0.10)')} />
        <button type="submit" disabled={submitting} style={{ ...btnBase, background: '#f5f0e8', color: '#0f0f0f', opacity: submitting ? 0.75 : 1 }} onMouseOver={e => !submitting && (e.currentTarget.style.background = '#ece6dd')} onMouseOut={e => (e.currentTarget.style.background = '#f5f0e8')}>
          {submitting ? 'Connecting...' : 'Continue with email'}
        </button>
      </form>
      <button style={{ ...btnBase, background: 'transparent', border: '1px solid rgba(255,255,255,0.08)', color: '#8a8a8a', marginTop: '14px', fontSize: '13px' }} onMouseOver={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.16)')} onMouseOut={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)')}>
        <AppleIcon /> Download desktop app
      </button>
    </div>
  );
};

const OAuthCallbackPage: React.FC = () => {
  const { handleCallback } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    if (code && state) {
      handleCallback(code, state)
        .then(() => navigate('/', { replace: true }))
        .catch(() => navigate('/login?error=callback_failed', { replace: true }));
    } else {
      navigate('/login?error=missing_params', { replace: true });
    }
  }, [searchParams, handleCallback, navigate]);

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ width: '32px', height: '32px', margin: '0 auto 20px', border: '2px solid rgba(255,255,255,0.08)', borderTop: '2px solid #d97757', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <p style={{ fontFamily: 'var(--serif)', fontSize: '20px', color: '#f5f0e8', marginBottom: '8px' }}>Verifying...</p>
      <p style={{ fontSize: '13px', color: '#8a8a8a' }}>Completing authentication</p>
    </div>
  );
};

// ── Application Pages ─────────────────────────────────────────────────────────

const DashboardPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeJobId = searchParams.get('job_id');
  const requirement = searchParams.get('q') || '';
  const { triggerRefreshExecutions } = useOutletContext<AppOutletContext>();
  
  const { status, stepText } = useJobPoller(activeJobId);

  // If a job just finished, refresh the sidebar
  useEffect(() => {
    if (status?.status === 'finished' || status?.status === 'failed') {
      triggerRefreshExecutions();
    }
  }, [status?.status, triggerRefreshExecutions]);

  const handleSubmit = async (prompt: string) => {
    try {
      const res = await executionsApi.generate(prompt);
      setSearchParams({ job_id: res.job_id, q: prompt });
    } catch (err) {
      console.error('Failed to submit job', err);
    }
  };

  // 1. Idle state (no active job) — centered prompt
  if (!activeJobId) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0 24px', animation: 'fade-in var(--duration-normal)' }}>
        <h2 style={{ fontFamily: 'var(--serif)', fontSize: '32px', marginBottom: '32px', color: 'var(--text-primary)' }}>
          What would you like to build?
        </h2>
        <PromptInput onSubmit={handleSubmit} autoFocus />
      </div>
    );
  }

  const isRunning = status?.status === 'queued' || status?.status === 'started';

  // 2. Active job state — Chat-like view with prompt bar at the bottom
  return (
    <div style={{ flex: 1, padding: '32px 24px 24px', display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <ExecutionChat
          requirement={requirement}
          jobStatus={status}
          stepText={stepText}
          executionDetail={null}
        />
      </div>
      <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
        <PromptInput onSubmit={handleSubmit} disabled={isRunning} autoFocus={!isRunning} />
      </div>
    </div>
  );
};

const ExecutionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<ExecutionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    executionsApi.get(id)
      .then(data => {
        setDetail(data);
        setError(null);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (prompt: string) => {
    try {
      const res = await executionsApi.generate(prompt);
      navigate(`/?job_id=${res.job_id}&q=${encodeURIComponent(prompt)}`);
    } catch (err) {
      console.error('Failed to submit job', err);
    }
  };

  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        Loading execution...
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--red)' }}>
        {error || 'Execution not found'}
      </div>
    );
  }

  return (
    <div style={{ flex: 1, padding: '32px 24px 24px', display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <ExecutionChat
          requirement={detail.requirement}
          jobStatus={null}
          executionDetail={detail}
        />
      </div>
      <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
        <PromptInput onSubmit={handleSubmit} />
      </div>
    </div>
  );
};

// ── Router ────────────────────────────────────────────────────────────────────

export const AppRoutes: React.FC = () => (
  <Routes>
    <Route element={<AuthLayout />}>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<OAuthCallbackPage />} />
    </Route>
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/executions/:id" element={<ExecutionDetailPage />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);
