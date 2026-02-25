import React from 'react';

interface Props { alerts: any[]; }

const AlertsFeed: React.FC<Props> = ({ alerts }) => {
  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="text-sm font-semibold mb-2">Alerts Feed</h3>
      <ul className="text-sm text-gray-700 max-h-64 overflow-y-auto">
        {alerts.length ? alerts.map((a, i) => <li key={i} className="border-b py-1">{a.message || JSON.stringify(a)}</li>) :
        <li className="text-gray-400">No alerts yet</li>}
      </ul>
    </div>
  );
};

export default AlertsFeed;
