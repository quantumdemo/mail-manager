import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, AlertTriangle, CheckCircle, Database, Trash2 } from 'lucide-react';
import socket from '../socket';

const Dashboard: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [summary, setSummary] = useState({
    total_scanned: 0,
    estimated_size: 0,
    potential_savings: 0
  });

  useEffect(() => {
    // Fetch initial data if scan was already completed
    fetch('/api/emails/data')
      .then(res => res.json())
      .then(data => {
        if (data.emails && data.emails.length > 0) {
          setSummary({
            total_scanned: data.emails.length,
            estimated_size: data.emails.reduce((acc: number, e: any) => acc + e.size, 0),
            potential_savings: data.emails.reduce((acc: number, e: any) => acc + e.size, 0) * 0.4
          });
          setProgress(100);
        }
      });

    const onProgress = (data: any) => {
      console.log('Scan progress received:', data);
      setProgress(data.progress);
      setSummary(prev => ({
        ...prev,
        total_scanned: data.count
      }));
    };

    const onComplete = (data: any) => {
      console.log('Scan complete received:', data);
      setIsScanning(false);
      setProgress(100);
      setSummary({
        total_scanned: data.total_count,
        estimated_size: data.total_size,
        potential_savings: data.total_size * 0.4
      });
    };

    socket.on('scan_progress', onProgress);
    socket.on('scan_complete', onComplete);

    return () => {
      socket.off('scan_progress', onProgress);
      socket.off('scan_complete', onComplete);
    };
  }, []);

  const handleStartScan = () => {
    if (!socket.connected) {
      alert("Still connecting to server... Please wait a moment.");
      return;
    }

    setIsScanning(true);
    setProgress(0);
    fetch(`/api/emails/scan?sid=${socket.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ months: 6 })
    }).catch(err => {
      console.error("Failed to start scan:", err);
      setIsScanning(false);
    });
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl">
              <Database size={24} />
            </div>
            {isScanning && <span className="animate-pulse text-xs text-blue-500 font-medium">Scanning...</span>}
          </div>
          <h3 className="text-slate-500 dark:text-slate-400 text-sm font-medium">Emails Scanned</h3>
          <p className="text-3xl font-bold mt-1">{summary.total_scanned.toLocaleString()}</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-xl">
              <Database size={24} />
            </div>
          </div>
          <h3 className="text-slate-500 dark:text-slate-400 text-sm font-medium">Estimated Storage</h3>
          <p className="text-3xl font-bold mt-1">{formatSize(summary.estimated_size)}</p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-xl">
              <Trash2 size={24} />
            </div>
          </div>
          <h3 className="text-slate-500 dark:text-slate-400 text-sm font-medium">Potential Savings</h3>
          <p className="text-3xl font-bold mt-1 text-green-600 dark:text-green-400">{formatSize(summary.potential_savings)}</p>
        </div>
      </div>

      {/* Main Action Area */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
        <div className="p-12 text-center space-y-6">
          {!isScanning && progress === 0 ? (
            <>
              <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center mx-auto mb-6">
                <Play size={40} fill="currentColor" />
              </div>
              <div className="space-y-2">
                <h2 className="text-3xl font-bold">Ready to analyze your inbox?</h2>
                <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto">
                  We'll fetch metadata for the last 6 months to help you identify storage-heavy emails.
                </p>
              </div>
              <button
                onClick={handleStartScan}
                className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-lg transition-all transform hover:scale-105 shadow-lg shadow-primary-500/25"
              >
                Start Scanning
              </button>
            </>
          ) : (
            <div className="max-w-xl mx-auto space-y-8 py-8">
               <div className="space-y-4">
                  <div className="flex justify-between text-sm font-medium">
                    <span>Scanning metadata...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full h-4 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-600 transition-all duration-500 ease-out rounded-full"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
               </div>
               <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl text-left border border-slate-100 dark:border-slate-700">
                    <CheckCircle className="text-green-500 mb-2" size={20} />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Security</p>
                    <p className="text-sm font-semibold">Metadata only fetch</p>
                  </div>
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl text-left border border-slate-100 dark:border-slate-700">
                    <ShieldCheck className="text-blue-500 mb-2" size={20} />
                    <p className="text-xs text-slate-500 dark:text-slate-400">Privacy</p>
                    <p className="text-sm font-semibold">Stateless processing</p>
                  </div>
               </div>
               {progress === 100 && (
                 <button
                   onClick={handleStartScan}
                   className="flex items-center gap-2 mx-auto text-slate-500 hover:text-primary-600 transition-colors"
                 >
                   <RotateCcw size={16} />
                   Rescan Inbox
                 </button>
               )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

// Temporary placeholder for missing component
const ShieldCheck = ({ size, className }: any) => <Database size={size} className={className} />;
