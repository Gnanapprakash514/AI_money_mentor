import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Onboarding from './pages/Onboarding'
import FIREPlanner from './pages/FIREPlanner'
import TaxWizard from './pages/TaxWizard'
import HealthScore from './pages/HealthScore'
import CouplePlanner from './pages/CouplePlanner'
import { fetchSavedProfile } from './api/client'

function App() {
  useEffect(() => {
    fetchSavedProfile().catch(() => undefined)
  }, [])

  return (
    <Routes>
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="fire" element={<FIREPlanner />} />
        <Route path="tax" element={<TaxWizard />} />
        <Route path="score" element={<HealthScore />} />
        <Route path="couple" element={<CouplePlanner />} />
      </Route>
    </Routes>
  )
}

export default App
