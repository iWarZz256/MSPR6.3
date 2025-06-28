import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import PandemicDashboard from './PandemicDashboard'
import AdminPage from './AdminPage'
import ContinentsAdmin from './ContinentsAdmin'
import FamillesAdmin from './FamillesAdmin'
import PandemiesAdmin from './PandemiesAdmin'
import PaysAdmin from './PaysAdmin'
import VirusAdmin from './VirusAdmin'
import MobileDashboard from './MobileDashboard'
import LoginPage from './LoginPage'
import PrivateRoute from './components/PrivateRoute'

// Redirection auto mobile
function MobileRedirector() {
  const navigate = useNavigate()

  useEffect(() => {
    const isMobile = window.innerWidth < 768
    if (isMobile && window.location.pathname === '/') {
      navigate('/mobile')
    }
  }, [navigate])

  return null
}

function App() {
  return (
    <BrowserRouter>
      <MobileRedirector />
      <Routes>
        {/* Publiques */}
        <Route path="/login" element={<LoginPage />} />
        {/* Protégées */}
        <Route path="/" element={<PrivateRoute><PandemicDashboard /></PrivateRoute>} />
        <Route path="/mobile" element={<MobileDashboard />} />
        <Route path="/admin" element={<PrivateRoute><AdminPage /></PrivateRoute>} />
        <Route path="/admin/continents" element={<PrivateRoute><ContinentsAdmin /></PrivateRoute>} />
        <Route path="/admin/familles" element={<PrivateRoute><FamillesAdmin /></PrivateRoute>} />
        <Route path="/admin/pandemies" element={<PrivateRoute><PandemiesAdmin /></PrivateRoute>} />
        <Route path="/admin/pays" element={<PrivateRoute><PaysAdmin /></PrivateRoute>} />
        <Route path="/admin/virus" element={<PrivateRoute><VirusAdmin /></PrivateRoute>} />

        {/* Fallback */}
        <Route path="*" element={<div>Cette route n'existe pas</div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
