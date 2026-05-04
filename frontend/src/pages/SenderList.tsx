import React, { useState, useEffect } from 'react';
import { Search, Filter, Trash2, ChevronRight, Info, AlertCircle, CheckCircle, Mail } from 'lucide-react';

interface Group {
  sender: string;
  count: number;
  total_size: number;
  emails: any[];
}

interface Recommendation {
  label: 'safe' | 'review' | 'keep';
  confidence: number;
  explanation: string;
}

const SenderList: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [recommendations, setRecommendations] = useState<Record<string, Recommendation>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);

  useEffect(() => {
    fetch('/api/emails/data')
      .then(res => res.json())
      .then(data => {
        setGroups(data.groups);
        setRecommendations(data.recommendations);
        setIsLoading(false);
      });
  }, []);

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getRecommendation = (senderEmails: any[]) => {
    // For simplicity, take the first one or average
    const firstId = senderEmails[0]?.id;
    return recommendations[firstId] || { label: 'keep', confidence: 0, explanation: 'Analyzing...' };
  };

  const filteredGroups = groups.filter(g =>
    g.sender.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <div>Loading sender data...</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* List Panel */}
      <div className="lg:col-span-2 space-y-6">
        <div className="flex items-center gap-4 bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <Search className="text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Search senders or domains..."
            className="flex-1 bg-transparent border-none focus:outline-none"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Filter className="text-slate-400" size={20} />
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[600px] md:min-w-full">
            <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-4 md:px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Sender</th>
                <th className="px-4 md:px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Count</th>
                <th className="px-4 md:px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Size</th>
                <th className="hidden sm:table-cell px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-4 md:px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filteredGroups.map((group) => {
                const rec = getRecommendation(group.emails);
                return (
                  <tr
                    key={group.sender}
                    onClick={() => setSelectedGroup(group)}
                    className={`cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ${selectedGroup?.sender === group.sender ? 'bg-primary-50 dark:bg-primary-900/10' : ''}`}
                  >
                    <td className="px-4 md:px-6 py-4 font-medium truncate max-w-[150px] md:max-w-xs">{group.sender}</td>
                    <td className="px-4 md:px-6 py-4 text-right text-slate-500">{group.count}</td>
                    <td className="px-4 md:px-6 py-4 text-right font-semibold">{formatSize(group.total_size)}</td>
                    <td className="hidden sm:table-cell px-6 py-4">
                      {rec.label === 'safe' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
                          <CheckCircle size={12} /> Safe to Delete
                        </span>
                      )}
                      {rec.label === 'review' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400">
                          <AlertCircle size={12} /> Review
                        </span>
                      )}
                      {rec.label === 'keep' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-400">
                           Keep
                        </span>
                      )}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-right">
                      <ChevronRight size={20} className="text-slate-300 ml-auto" />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Panel */}
      <div className="space-y-6">
        {selectedGroup ? (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sticky top-24">
            <h3 className="text-xl font-bold mb-4">Sender Details</h3>
            <div className="space-y-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
                <p className="text-xs text-slate-500 mb-1">Sender Address</p>
                <p className="font-medium break-all">{selectedGroup.sender}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                 <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
                    <p className="text-xs text-slate-500 mb-1">Emails</p>
                    <p className="text-lg font-bold">{selectedGroup.count}</p>
                 </div>
                 <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
                    <p className="text-xs text-slate-500 mb-1">Storage Used</p>
                    <p className="text-lg font-bold">{formatSize(selectedGroup.total_size)}</p>
                 </div>
              </div>

              <div className="p-4 border-2 border-slate-100 dark:border-slate-800 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-primary-600 font-bold text-sm">
                  <Info size={16} /> AI Recommendation
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {getRecommendation(selectedGroup.emails).explanation}
                </p>
              </div>

              <button
                onClick={() => {
                  const ids = selectedGroup.emails.map(e => e.id);
                  const provider = selectedGroup.emails[0]?.provider;
                  fetch('/api/emails/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids, provider })
                  })
                  .then(res => res.json())
                  .then(data => {
                    if (data.status === 'success') {
                      alert(`Successfully moved ${data.deleted_count} emails to trash.`);
                      window.location.reload();
                    }
                  });
                }}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-red-500/20"
              >
                <Trash2 size={20} />
                Bulk Move to Trash
              </button>
              <p className="text-[10px] text-center text-slate-400">
                This will move all {selectedGroup.count} emails from this sender to your trash.
              </p>
            </div>
          </div>
        ) : (
          <div className="h-64 flex flex-col items-center justify-center text-center p-6 bg-slate-50 dark:bg-slate-900/50 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800 text-slate-400">
             <Mail size={40} className="mb-4 opacity-20" />
             <p className="text-sm">Select a sender to view details and recommendations</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SenderList;
