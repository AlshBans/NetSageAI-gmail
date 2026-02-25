import React, { useState } from 'react';
import { login } from '../api';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setError('');
    const result = await login(email, password);
    if(result.success){
      localStorage.setItem('token', result.token || 'demo-token');
      localStorage.setItem('monitor_email', email);
      localStorage.setItem('monitor_pass', password);
      navigate('/dashboard');
    } else {
      setError('Login failed: ' + result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-indigo-700">
      <div className="bg-white/95 rounded-xl shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-2 text-center">NetSageAI-MailGuard</h2>
        <p className="text-sm text-gray-600 text-center mb-6">Secure Gmail Monitoring Dashboard</p>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Email Address</label>
            <input required type="email" value={email} onChange={e=>setEmail(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded"/>
          </div>
          <div>
            <label className="text-sm font-medium">App Password</label>
            <input required type="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded"/>
          </div>
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center">
              <input type="checkbox" checked={remember} onChange={e=>setRemember(e.target.checked)} className="mr-2"/>
              Remember Me
            </label>
            <a className="text-blue-600" href="#">Forgot Password?</a>
          </div>
          <button className="w-full bg-green-600 text-white py-2 rounded font-semibold">Sign In</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
