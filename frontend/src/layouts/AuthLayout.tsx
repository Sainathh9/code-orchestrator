import React from 'react';
import { Outlet } from 'react-router-dom';
import loginIllustration from '../assets/login_illustration.png';

/**
 * Claude-style split-screen AuthLayout.
 * Left: dark panel with login form, centered.
 * Right: vintage illustration card on dark background.
 */
export const AuthLayout: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background: '#0f0f0f',
    }}>
      {/* Left Panel — Login Content */}
      <div style={{
        flex: '0 0 50%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '60px 80px',
        boxSizing: 'border-box',
        position: 'relative',
      }}>
        <Outlet />
      </div>

      {/* Right Panel — Illustration Card */}
      <div style={{
        flex: '0 0 50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px',
        boxSizing: 'border-box',
      }}>
        <div style={{
          width: '100%',
          maxWidth: '500px',
          aspectRatio: '1 / 1.05',
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 32px 80px rgba(0,0,0,0.6)',
          position: 'relative',
        }}>
          <img
            src={loginIllustration}
            alt="Vintage botanical illustration"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center top',
              display: 'block',
            }}
          />
          {/* Very subtle overlay to give a slight warm tint */}
          <div style={{
            position: 'absolute',
            inset: 0,
            background: 'rgba(15, 10, 5, 0.06)',
            pointerEvents: 'none',
          }} />
        </div>
      </div>
    </div>
  );
};
