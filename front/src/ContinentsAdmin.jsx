import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import 'leaflet/dist/leaflet.css'
import './modern_medical_dashboard.css'

export default function ContinentsAdmin() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [modalType, setModalType] = useState(null)
  const [selectedContinent, setSelectedContinent] = useState(null)
  const [newContinentName, setNewContinentName] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [continents, setContinents] = useState([
    { id: 'AF', name: 'Afrique' },
    { id: 'AN', name: 'Antarctique' },
    { id: 'AS', name: 'Asie' },
    { id: 'EU', name: 'Europe' },
    { id: 'NA', name: 'Amérique du Nord' },
    { id: 'OC', name: 'Océanie' },
    { id: 'SA', name: 'Amérique du Sud' },
  ])
  const location = useLocation()

  //test docker
  const cards = [
    { title: "Continents", to: "/admin/continents", icon: "🌍" },
    { title: "Familles", to: "/admin/familles", icon: "🧬" },
    { title: "Pandémies", to: "/admin/pandemies", icon: "🦠" },
    { title: "Pays", to: "/admin/pays", icon: "🏛️" },
    { title: "Virus", to: "/admin/virus", icon: "🧫" },
  ]

  useEffect(() => {
    document.body.style.overflow = (sidebarOpen || modalType) ? 'hidden' : 'auto'
    return () => { document.body.style.overflow = 'auto' }
  }, [sidebarOpen, modalType])

  const openChoiceModal = (continent) => {
    setSelectedContinent(continent)
    setModalType('choice')
  }

  const openEditModal = (continent) => {
    setSelectedContinent(continent)
    setNewContinentName(continent.name)
    setModalType('edit')
  }

  const openDeleteModal = (continent) => {
    setSelectedContinent(continent)
    setModalType('delete')
  }

  const handleSaveEdit = () => {
    if (newContinentName.trim() === '') return
    setContinents(continents.map(c =>
      c.id === selectedContinent.id ? { ...c, name: newContinentName } : c
    ))
    closeModal()
  }

  const handleConfirmDelete = () => {
    setContinents(continents.filter(c => c.id !== selectedContinent.id))
    closeModal()
  }

  const openAddModal = () => {
    setNewContinentName('')
    setModalType('add')
  }

  const handleAddContinent = () => {
    if (newContinentName.trim() === '') return
    const id = newContinentName.slice(0, 2).toUpperCase()
    if (continents.some(c => c.id === id)) {
      alert(`Le code ${id} existe déjà.`)
      return
    }
    setContinents([...continents, { id, name: newContinentName }])
    closeModal()
  }

  const closeModal = () => {
    setModalType(null)
    setSelectedContinent(null)
    setNewContinentName('')
  }

  const filteredContinents = continents.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="relative flex flex-col md:flex-row h-screen bg-gray-100 overflow-x-hidden">
      {(sidebarOpen || modalType) && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-30 md:hidden"
          onClick={() => { setSidebarOpen(false); closeModal() }}
        />
      )}

      <aside className={`fixed md:relative top-0 left-0 h-full w-64 bg-blue-800 text-white p-4 space-y-6 z-40 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 transition-transform duration-300 ease-in-out`}>
        <h2 className="text-center text-2xl font-bold">PVDH</h2>
        <nav className="space-y-2 mt-6">
          <Link to="/" className={`block py-2 px-4 rounded-lg transition ${location.pathname === '/' ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}>📊 Dashboard</Link>
          <div className={`block py-2 px-4 rounded-lg transition ${location.pathname.startsWith('/admin') ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}>⚙️ Administration</div>
          {location.pathname.startsWith('/admin') && (
            <div className="ml-4 space-y-1">
              {cards.map(card => (
                <Link key={card.to} to={card.to} className={`flex items-center gap-2 py-1 px-2 rounded-lg text-sm transition ${location.pathname === card.to ? 'bg-blue-700 font-bold' : 'hover:bg-blue-600'}`}>
                  <span className="text-lg">{card.icon}</span> {card.title}
                </Link>
              ))}
            </div>
          )}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="flex items-center justify-between bg-white p-4 shadow-md md:hidden">
          <h1 className="text-xl font-bold">Gestion des Continents</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)}>
            <svg className="w-8 h-8" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </button>
        </header>

        <main className="p-4 md:p-6 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <h1 className="hidden md:block text-3xl font-bold">Gestion des Continents</h1>
            <div className="flex flex-col md:flex-row gap-2 items-stretch md:items-center">
              <input
                type="text"
                placeholder="🔍 Rechercher un continent..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring focus:border-blue-300"
              />
              <button
                onClick={openAddModal}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
              >
                ➕ Ajouter un continent
              </button>
            </div>
          </div>

          <div className="hidden md:block bg-white rounded-2xl shadow overflow-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredContinents.map((continent) => (
                  <tr key={continent.id}>
                    <td className="px-6 py-4 whitespace-nowrap">{continent.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{continent.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button onClick={() => openEditModal(continent)} className="text-blue-600 hover:text-blue-900 mr-4">✏️ Modifier</button>
                      <button onClick={() => openDeleteModal(continent)} className="text-red-600 hover:text-red-900">🗑️ Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="block md:hidden space-y-4">
            {filteredContinents.map((continent) => (
              <div key={continent.id} onClick={() => openChoiceModal(continent)} className="cursor-pointer bg-white rounded-xl p-4 shadow flex flex-col gap-2 hover:bg-gray-100">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-lg">{continent.name}</div>
                  <div className="text-sm text-gray-500">{continent.id}</div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>

      {modalType && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-80 space-y-4">
            {modalType === 'choice' && (
              <>
                <h2 className="text-xl font-bold">Que faire ?</h2>
                <div className="flex flex-col gap-3">
                  <button onClick={() => openEditModal(selectedContinent)} className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700">✏️ Modifier</button>
                  <button onClick={() => openDeleteModal(selectedContinent)} className="bg-red-600 text-white py-2 rounded hover:bg-red-700">🗑️ Supprimer</button>
                  <button onClick={closeModal} className="bg-gray-300 text-black py-2 rounded hover:bg-gray-400">Annuler</button>
                </div>
              </>
            )}
            {modalType === 'edit' && (
              <>
                <h2 className="text-xl font-bold">Modifier le continent</h2>
                <input
                  type="text"
                  value={newContinentName}
                  onChange={(e) => setNewContinentName(e.target.value)}
                  className="w-full border border-gray-300 rounded p-2"
                />
                <div className="flex justify-end gap-2">
                  <button onClick={closeModal} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Annuler</button>
                  <button onClick={handleSaveEdit} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Sauvegarder</button>
                </div>
              </>
            )}
            {modalType === 'delete' && (
              <>
                <h2 className="text-xl font-bold text-red-600">Confirmer la suppression ?</h2>
                <div className="flex justify-end gap-2">
                  <button onClick={closeModal} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Annuler</button>
                  <button onClick={handleConfirmDelete} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Supprimer</button>
                </div>
              </>
            )}
            {modalType === 'add' && (
              <>
                <h2 className="text-xl font-bold">Ajouter un continent</h2>
                <input
                  type="text"
                  placeholder="Nom du continent"
                  value={newContinentName}
                  onChange={(e) => setNewContinentName(e.target.value)}
                  className="w-full border border-gray-300 rounded p-2"
                />
                <div className="flex justify-end gap-2">
                  <button onClick={closeModal} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Annuler</button>
                  <button onClick={handleAddContinent} className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Ajouter</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}