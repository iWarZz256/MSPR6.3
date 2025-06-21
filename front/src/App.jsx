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
        <Route path="/" element={<PandemicDashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/admin/continents" element={<ContinentsAdmin />} />
        <Route path="/admin/familles" element={<FamillesAdmin />} />
        <Route path="/admin/pandemies" element={<PandemiesAdmin />} />
        <Route path="/admin/pays" element={<PaysAdmin />} />
        <Route path="/admin/virus" element={<VirusAdmin />} />
        <Route path="/mobile" element={<MobileDashboard />} />
        <Route path="*" element={<div>Cette route n'existe pas</div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
