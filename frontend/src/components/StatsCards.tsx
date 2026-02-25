import React from 'react';

interface Props {
  totalEmails: number;
  suspicious: number;
  avgSizeKB: number;
  attachments: number;
}

const StatsCards: React.FC<Props> = ({ totalEmails, suspicious, avgSizeKB, attachments }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-white p-4 rounded shadow text-center">
        <div className="text-gray-500 text-sm">Total Emails</div>
        <div className="text-xl font-bold">{totalEmails}</div>
      </div>
      <div className="bg-white p-4 rounded shadow text-center">
        <div className="text-gray-500 text-sm">Suspicious</div>
        <div className="text-xl font-bold">{suspicious}</div>
      </div>
      <div className="bg-white p-4 rounded shadow text-center">
        <div className="text-gray-500 text-sm">Avg Email Size (KB)</div>
        <div className="text-xl font-bold">{avgSizeKB.toFixed(2)}</div>
      </div>
      <div className="bg-white p-4 rounded shadow text-center">
        <div className="text-gray-500 text-sm">With Attachments</div>
        <div className="text-xl font-bold">{attachments}</div>
      </div>
    </div>
  );
};

export default StatsCards;
