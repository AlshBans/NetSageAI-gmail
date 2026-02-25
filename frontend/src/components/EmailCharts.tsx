import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

export const SmallLine: React.FC<{data:any}> = ({ data }) => <div className="bg-white rounded shadow p-4"><Line data={data} /></div>;
export const SmallBar: React.FC<{data:any}> = ({ data }) => <div className="bg-white rounded shadow p-4"><Bar data={data} /></div>;
export const SmallDoughnut: React.FC<{data:any}> = ({ data }) => <div className="bg-white rounded shadow p-4"><Doughnut data={data} /></div>;
