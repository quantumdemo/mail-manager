import React from 'react';
import { Chrome as Google, Landmark as Microsoft, Mail, ShieldCheck, Zap } from 'lucide-react';
import logo from '../assets/logo.jpg';

interface LandingProps {
  onAuthSuccess: () => void;
}

const Landing: React.FC<LandingProps> = ({ onAuthSuccess }) => {
  const handleLogin = (provider: 'gmail' | 'outlook') => {
    fetch(`/api/auth/${provider}/login`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to initiate login');
        return res.json();
      })
      .then(data => {
        if (data.url) {
          window.location.href = data.url;
        } else {
          console.error('No redirect URL received');
          alert('Login configuration error. Please check backend environment variables.');
        }
      })
      .catch(err => {
        console.error(err);
        alert('Could not connect to the authentication service. Make sure the backend is running and configured.');
      });
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <img src={logo} alt="Logo" className="w-10 h-10 rounded-lg object-cover" />
          <span className="text-xl font-bold text-slate-900 dark:text-white">Mail Manager</span>
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-3xl space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
              Clean your inbox. <br />
              <span className="text-primary-600">Reclaim your peace of mind.</span>
            </h1>
            <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Privacy-first, stateless email analysis. Identify bulky emails, find newsletters, and clean up your storage in seconds.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => handleLogin('gmail')}
              className="w-full sm:w-auto flex items-center justify-center gap-3 px-8 py-4 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-xl font-semibold text-slate-900 dark:text-white hover:border-primary-500 transition-all shadow-sm"
            >
              <Google className="text-red-500" />
              Connect Gmail
            </button>
            <button
              onClick={() => handleLogin('outlook')}
              className="w-full sm:w-auto flex items-center justify-center gap-3 px-8 py-4 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-xl font-semibold text-slate-900 dark:text-white hover:border-primary-500 transition-all shadow-sm"
            >
              <Microsoft className="text-blue-500" />
              Connect Outlook
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-16">
            <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm text-left">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-xl flex items-center justify-center mb-4">
                <ShieldCheck size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2">Stateless & Secure</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">We don't store your emails or tokens. Your data never leaves your session.</p>
            </div>
            <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm text-left">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-xl flex items-center justify-center mb-4">
                <Zap size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2">Real-time Analysis</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Lightning fast metadata scan with real-time grouping by sender and domain.</p>
            </div>
            <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm text-left">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center mb-4">
                <Mail size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2">AI Recommendations</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Smart heuristics identify newsletters and bulk senders safe to delete.</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="p-8 border-t border-slate-200 dark:border-slate-800 text-center text-slate-500 text-sm">
        &copy; {new Date().getFullYear()} Mail Manager. Built with privacy in mind.
      </footer>
    </div>
  );
};

export default Landing;
