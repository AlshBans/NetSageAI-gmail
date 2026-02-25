import React, { useEffect, useState } from 'react';
import * as api from '../api';
import StatsCards from '../components/StatsCards';
import RecentEmails from '../components/RecentEmails';
import AlertsFeed from '../components/AlertsFeed';
import { SmallLine, SmallBar, SmallDoughnut } from '../components/EmailCharts';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>({ total_emails:0, total_anomalies:0, avg_email_size:0, emails_with_attachments:0, top_senders:[] });
  const [alerts, setAlerts] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(()=>{
    const token = localStorage.getItem('token');
    if(!token) navigate('/');
    (async ()=>{
      try{ const s = await api.getStats(); setStats(s); }catch(e){}
      try{ const a = await api.getAlerts(50); setAlerts(a); }catch(e){}
    })();

    const ws = new WebSocket('ws://127.0.0.1:8000/ws/events');
    ws.onmessage = (ev) => {
      const d = JSON.parse(ev.data);
      if(d.type === 'alert'){
        setAlerts(prev => [d.alert, ...prev].slice(0,200));
      }
    };
    return ()=> ws.close();
  },[navigate]);

  const lineData = {
    labels:['-30m','-20m','-10m','-5m','now'],
    datasets:[{ label:'Emails/min', data:[3,5,4,9,7], borderColor:'#3b82f6', backgroundColor:'rgba(59,130,246,0.12)', fill:true, tension:0.3 }]
  };
  const doughData = {
    labels:['Normal','Suspicious'],
    datasets:[{ data:[(stats.total_emails - stats.total_anomalies)||0, stats.total_anomalies||0], backgroundColor:['#22c55e','#ef4444'] }]
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold">NetSageAI-MailGuard</h1>
          <p className="text-sm text-gray-500">Secure Gmail Monitoring Dashboard</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-700">{localStorage.getItem('monitor_email') || ''}</div>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('monitor_email');
              localStorage.removeItem('monitor_pass');
              navigate('/');
            }}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>

      <StatsCards totalEmails={stats.total_emails} suspicious={stats.total_anomalies} avgSizeKB={(stats.avg_email_size/1024)||0} attachments={stats.emails_with_attachments}/>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
        <SmallLine data={lineData}/>
        <SmallBar data={lineData}/>
        <SmallDoughnut data={doughData}/>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <RecentEmails />
        </div>
        <div className="w-full">
          <AlertsFeed alerts={alerts}/>
          <div className="bg-white dark:bg-gray-800 rounded shadow p-4 mt-4">
            <h3 className="text-sm font-semibold mb-2">Controls</h3>
            <div className="space-y-2">
              <button onClick={async ()=>{
                const email = localStorage.getItem('monitor_email');
                const pass = localStorage.getItem('monitor_pass');
                await api.startMonitor(email || '', pass || '');
              }} className="w-full px-3 py-2 bg-blue-600 text-white rounded">Start Monitor</button>
              <button onClick={async ()=>{ await api.getAlerts(); }} className="w-full px-3 py-2 bg-gray-200 rounded">Refresh Alerts</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
