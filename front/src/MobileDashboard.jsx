import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './modern_medical_dashboard.css'

const casesByCountry = {
  FR: 450000, DE: 120000, IT: 850000, US: 950000, CN: 5000,
  BR: 670000, IN: 300000, RU: 40000, CA: 25000, JP: 1000,
  MX: 760000, ZA: 8900, NO: 0, SE: 0, FI: 0,
}
const countryNames = {
  FR: "France",
  DE: "Germany",
  IT: "Italy",
  US: "United States",
  CN: "China",
  BR: "Brazil",
  IN: "India",
  RU: "Russia",
  CA: "Canada",
  JP: "Japan",
  MX: "Mexico",
  ZA: "South Africa",
  NO: "Norway",
  SE: "Sweden",
  FI: "Finland"
}


const evolutionData = [
  { year: '2019', cases: 2000 },
  { year: '2020', cases: 5000000 },
  { year: '2021', cases: 6000000 },
  { year: '2022', cases: 4000000 },
  { year: '2023', cases: 2000000 },
  { year: '2024', cases: 1000000 },
]

const continentCases = [
  { name: 'Europe', cases: 1600000 },
  { name: 'Asie', cases: 3050000 },
  { name: 'Amérique', cases: 1730000 },
  { name: 'Afrique', cases: 8900 },
  { name: 'Océanie', cases: 1000 },
]

const virusStats = [
  { name: 'COVID-19', cases: 6000000 },
  { name: 'Grippe H1N1', cases: 1200000 },
  { name: 'Ebola', cases: 30000 },
  { name: 'SARS', cases: 8000 },
  { name: 'Zika', cases: 5000 },
]

const virusVisuals = {
  "COVID-19": { icon: "🦠", color: "bg-red-100 text-red-800", bar: "bg-red-400" },
  "Grippe H1N1": { icon: "🤧", color: "bg-yellow-100 text-yellow-800", bar: "bg-yellow-400" },
  "Ebola": { icon: "🧬", color: "bg-purple-100 text-purple-800", bar: "bg-purple-500" },
  "SARS": { icon: "😷", color: "bg-blue-100 text-blue-800", bar: "bg-blue-400" },
  "Zika": { icon: "🦟", color: "bg-pink-100 text-pink-700", bar: "bg-pink-500" }
}


const getFlagEmoji = (countryCode) =>
  countryCode
    .toUpperCase()
    .replace(/./g, char => String.fromCodePoint(char.charCodeAt(0) + 127397));


export default function MobileDashboard() {
  const [activeCard, setActiveCard] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const [searchQuery, setSearchQuery] = useState('')


  const totalContinentCases = continentCases.reduce((a, b) => a + b.cases, 0)
  const totalVirusCases = virusStats.reduce((a, b) => a + b.cases, 0)

  return (
    <div className="relative flex flex-col h-screen bg-[#f8fafc] overflow-y-auto">

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar identique */}
      <aside className={`fixed top-0 left-0 h-full w-64 bg-blue-800 text-white p-4 z-40 transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <h2 className="text-center text-2xl font-bold">PVDH</h2>
        <nav className="mt-6 space-y-2">
          <Link to="/mobile" onClick={() => setSidebarOpen(false)} className={`block py-2 px-4 rounded-lg transition ${location.pathname === '/mobile' ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}>
            📊 Dashboard
          </Link>
          <Link to="/admin" onClick={() => setSidebarOpen(false)} className={`block py-2 px-4 rounded-lg transition ${location.pathname === '/admin' ? 'bg-blue-700 font-bold' : 'hover:bg-blue-700'}`}>
            ⚙️ Administration
          </Link>
        </nav>
      </aside>

      {/* Header modernisé */}
      <header className="sticky top-0 z-20 flex items-center justify-between bg-white p-4 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">📈 Tableau de bord</h1>
        <button onClick={() => setSidebarOpen(!sidebarOpen)}>
          <svg className="w-7 h-7 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M4 6h16M4 12h16M4 18h16" strokeWidth="2" />
          </svg>
        </button>
      </header>

      {/* Content */}
      <main className="p-5">
        {!activeCard ? (
          <div className="grid gap-4">
            {[
              { id: 'pays', label: 'Cas par pays 🌏', bg: 'bg-gradient-to-r from-blue-400 to-blue-600' },
              { id: 'evolution', label: 'Évolution temporelle ⏲️', bg: 'bg-gradient-to-r from-purple-400 to-purple-600' },
              { id: 'continent', label: 'Cas par continent 🌎', bg: 'bg-gradient-to-r from-green-400 to-green-600' },
              { id: 'virus', label: 'Répartition des virus 🦠', bg: 'bg-gradient-to-r from-pink-400 to-pink-600' },
            ].map(card => (
              <div key={card.id}
                onClick={() => setActiveCard(card.id)}
                className={`${card.bg} cursor-pointer text-white p-6 rounded-xl shadow-md transition transform hover:scale-105`}>
                <h2 className="text-lg font-semibold">{card.label}</h2>
              </div>
            ))}
          </div>
        ) : (
          <section className="space-y-4 animate-fadeIn">
            <div className="text-center ">
              <button
                onClick={() => setActiveCard(null)}
                className="bg-gray-800 hover:bg-gray-900 text-white px-6 py-2 rounded-full shadow-md transition">
                Accueil
              </button>

            </div>
            {activeCard === 'pays' && (
              <>


                <h2 className="text-xl font-bold">🌍 Cas par pays</h2>

                <input
                  type="text"
                  placeholder="Rechercher un pays..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full mt-2 mb-4 px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />

                {[...Object.entries(casesByCountry)]
                  .filter(([code]) => {
                    const name = countryNames[code] || ""
                    return (
                      code.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                  })
                  .sort((a, b) => b[1] - a[1])
                  .map(([code, count]) => (
                    <div key={code} className="bg-white p-4 rounded-xl shadow flex justify-between items-center">
                      <div className="font-medium flex items-center gap-2">
                        <span>{getFlagEmoji(code)}</span>
                        <span>{countryNames[code] || code}</span>
                        <span className="text-gray-400 text-xs">({code})</span>
                      </div>
                      <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                        {count.toLocaleString()} cas
                      </span>
                    </div>
                  ))}
              </>
            )}


            {activeCard === 'evolution' && (
              <>


                <h2 className="text-xl font-bold">📊 Évolution des cas par année</h2>

                {evolutionData.map((entry, index) => {
                  const prev = evolutionData[index - 1]
                  const diff = prev ? entry.cases - prev.cases : null
                  const diffPercent = prev ? ((diff / prev.cases) * 100).toFixed(1) : null
                  const isUp = diff > 0

                  return (
                    <div key={entry.year} className="space-y-1">
                      <div className="bg-white p-4 rounded-xl shadow flex justify-between">
                        <span>{entry.year}</span>
                        <span className="text-sm text-purple-700">{entry.cases.toLocaleString()} cas</span>
                      </div>

                      {index > 0 && (
                        <div className={`text-sm text-center font-medium ${isUp ? 'text-red-600' : 'text-green-600'}`}>
                          {isUp ? '🔺 Augmentation' : '🔻 Diminution'} de {Math.abs(diffPercent)}% par rapport à {prev.year}
                        </div>
                      )}
                    </div>
                  )
                })}
              </>
            )}

            {activeCard === 'continent' && (
              <>


                <h2 className="text-xl font-bold">🌐 Répartition par continent</h2>

                {([...continentCases]
                  .sort((a, b) => b.cases - a.cases))
                  .map(cont => {
                    const percent = ((cont.cases / totalContinentCases) * 100).toFixed(1)
                    const continentIcons = {
                      Europe: "🌍",
                      Asie: "🌏",
                      Amérique: "🌎",
                      Afrique: "🌍",
                      Océanie: "🌊"
                    }

                    return (
                      <div key={cont.name} className="bg-white p-4 rounded-xl shadow mb-4">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span>{continentIcons[cont.name]}</span>
                            <span>{cont.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
                              {percent}%
                            </span>
                            <span className="text-sm text-gray-500">
                              ({cont.cases.toLocaleString()} cas)
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </>
            )}

            {activeCard === 'virus' && (
              <>

                <h2 className="text-xl font-bold">🦠 Répartition des virus</h2>

                {[...virusStats]
                  .sort((a, b) => b.cases - a.cases)
                  .map(v => {
                    const percent = ((v.cases / totalVirusCases) * 100).toFixed(1)
                    const visuals = virusVisuals[v.name] || {}
                    return (
                      <div key={v.name} className="bg-white p-4 rounded-xl shadow mb-4">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span>{visuals.icon || "🧪"}</span>
                            <span>{v.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`text-sm px-3 py-1 rounded-full ${visuals.color || 'bg-gray-200 text-gray-800'}`}>
                              {percent}%
                            </span>
                            <span className="text-sm text-gray-500">
                              ({v.cases.toLocaleString()} cas)
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                          <div
                            className={`${visuals.bar || 'bg-gray-500'} h-2 rounded-full`}
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </>
            )}


          </section>
        )}
      </main>
    </div>
  )
}
