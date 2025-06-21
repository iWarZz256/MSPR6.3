import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import 'leaflet/dist/leaflet.css'
import './modern_medical_dashboard.css'

export default function AdminPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const cards = [
    { title: "Continents", to: "/admin/continents", icon: "🌍" },
    { title: "Familles", to: "/admin/familles", icon: "🧬" },
    { title: "Pandémies", to: "/admin/pandemies", icon: "🦠" },
    { title: "Pays", to: "/admin/pays", icon: "🏛️" },
    { title: "Virus", to: "/admin/virus", icon: "🧫" },
  ]

  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'auto'
    }
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [sidebarOpen])

  return (
    <div className="relative flex flex-col md:flex-row h-screen bg-gray-100 overflow-x-hidden">
      
      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed md:relative top-0 left-0 h-full w-64 bg-blue-800 text-white p-4 space-y-6 z-40 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 transition-transform duration-300 ease-in-out`}>
      <h2 className="text-center text-2xl font-bold">PVDH</h2>
        <nav className="space-y-2 mt-6">

          {/* Dashboard Link */}
          <Link
            to="/"
            onClick={() => setSidebarOpen(false)}
            className={`block py-2 px-4 rounded-lg transition ${location.pathname === '/' ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}
          >
            📊 Dashboard
          </Link>

          {/* Administration Link */}
          <div className={`block py-2 px-4 rounded-lg transition ${location.pathname.startsWith('/admin') ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}>
            ⚙️ Administration
          </div>

          {/* Sous-menu administration */}
          {location.pathname.startsWith('/admin') && (
            <div className="ml-4 space-y-1">
              {cards.map(card => (
                <Link
                  key={card.to}
                  to={card.to}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-2 py-1 px-2 rounded-lg text-sm transition hover:bg-blue-600 ${location.pathname === card.to ? 'font-semibold underline' : ''}`}
                >
                  <span className="text-lg">{card.icon}</span> {card.title}
                </Link>
              ))}
            </div>
          )}

          

        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Header */}
        <header className="flex items-center justify-between bg-white p-4 shadow-md md:hidden">
          <h1 className="text-xl font-bold">Espace Admin</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? (
              <svg className="w-8 h-8" viewBox="0 0 24 24">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : (
              <svg className="w-8 h-8" viewBox="0 0 24 24">
                <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
        </header>

        {/* Main Admin Content */}
        <main className="p-4 md:p-6 space-y-6">
          <h1 className="hidden md:block text-3xl font-bold mb-8">Espace Admin</h1>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {cards.map((card) => (
              <Link
                key={card.to}
                to={card.to}
                className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl shadow-md hover:shadow-lg transition"
              >
                <div className="text-5xl mb-4">{card.icon}</div>
                <div className="text-lg font-medium text-center">{card.title}</div>
              </Link>
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}
