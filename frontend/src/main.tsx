import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Login/>} />
        <Route path='/dashboard' element={
          <ProtectedRoute>
            <Dashboard/>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
