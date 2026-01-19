// Fichier React simplifié pour une version uniquement desktop du Dashboard
import { useState, useEffect, useRef } from 'react'
import countries from 'i18n-iso-countries'
import frLocale from 'i18n-iso-countries/langs/fr.json'
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import 'leaflet/dist/leaflet.css'
import './modern_medical_dashboard.css'
import WorldMap from './components/WorldMap'
import { Link, useLocation } from 'react-router-dom'
import LoadingScreen from './components/LoadingScreen'
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;


countries.registerLocale(frLocale)
const virusColors = {
  'covid-19': '#007BFF',     // bleu
  'variole du singe': '#28A745',  // vert
  'Ebola': '#DC3545',        // rouge
  'variole du singe': '#6F42C1',         // violet
  'Zika': '#17A2B8',         // turquoise
  'Inconnu': '#999999'       // gris
}



const continentComparisonData = [
  { name: 'Europe', cases: 1600000 },
  { name: 'Asie', cases: 3050000 },
  { name: 'Amérique', cases: 1730000 },
  { name: 'Afrique', cases: 8900 },
  { name: 'Océanie', cases: 1000 },
]

const virusPieData = [
  { name: 'COVID-19', value: 6000000 },
  { name: 'Grippe H1N1', value: 1200000 },
  { name: 'Ebola', value: 30000 },
  { name: 'SARS', value: 8000 },
  { name: 'Zika', value: 5000 },
]

const pieColors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AA336A']

export default function PandemicDashboard() {
  const [casesByDateByVirus, setCasesByDateByVirus] = useState({})
  const [modalCountry, setModalCountry] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedVirus, setSelectedVirus] = useState('COVID-19')
  const [geoData, setGeoData] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const mapRef = useRef(null)
  const [multiVirusMonthlyData, setMultiVirusMonthlyData] = useState([]);
  const [continentComparisonData, setContinentComparisonData] = useState([])
  const [virusPieData, setVirusPieData] = useState([])

  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token'); // ou sessionStorage si c’est ce que tu utilises
    navigate('/login'); // redirige vers la page de login
  };


  useEffect(() => {
    fetch(`${API_URL}/suivis/last-per-virus`)
      .then(res => res.json())
      .then(data => {
        const pie = data.map(item => ({
          name: item.virus,
          value: item.total_cas
        }))
        setVirusPieData(pie)
      })
      .catch(err => console.error("Erreur chargement pie data :", err))
  }, [])

  useEffect(() => {
    if (!selectedVirus) return;

    fetch(`${API_URL}/suivis/last-per-continent?pandemie=${encodeURIComponent(selectedVirus)}`)
      .then((res) => res.json())
      .then((data) => {
        const formatted = data
          .filter(item => item.continent && item.continent.toLowerCase() !== 'inconnu')
          .map(item => ({
            name: item.continent,
            cases: item.total_cas
          }))
        setContinentComparisonData(formatted)
      })
      .catch(err => console.error("Erreur chargement continents :", err))
  }, [selectedVirus]) // 🔁 mettre selectedVirus en dépendance





  useEffect(() => {
    setIsLoading(true)
    fetch(`${API_URL}/suivis`)
      .then((res) => res.json())
      .then((data) => {
        const structured = {}
        data.forEach(({ pays_iso, date_jour, total_cas, pandemie }) => {
          const virusName = pandemie || 'Inconnu'
          if (!structured[virusName]) structured[virusName] = {}
          if (!structured[virusName][date_jour]) structured[virusName][date_jour] = {}
          structured[virusName][date_jour][pays_iso.toUpperCase()] = total_cas
        })
        setCasesByDateByVirus(structured)

        if (structured['COVID-19']) {
          setSelectedVirus('COVID-19')
        } else {
          const firstVirus = Object.keys(structured)[0]
          if (firstVirus) setSelectedVirus(firstVirus)
        }

        setIsLoading(false) // ✅ Fini
      })
      .catch((err) => {
        console.error('Erreur chargement API :', err)
        setIsLoading(false) // ✅ Même en cas d'erreur, on stoppe le "loading"
      })
  }, [])


  useEffect(() => {
    const virusDates = Object.keys(casesByDateByVirus[selectedVirus] || {}).sort()
    if (!virusDates.includes(selectedDate)) {
      // Met à jour seulement si la date actuelle ne correspond pas au nouveau virus
      setSelectedDate(virusDates[0] || '')
    }
  }, [selectedVirus, casesByDateByVirus])
  const virusDates = Object.keys(casesByDateByVirus[selectedVirus] || {}).sort()

  useEffect(() => {
    const grouped = {}
    // Parcours de tous les virus
    Object.entries(casesByDateByVirus).forEach(([virus, dates]) => {
      Object.entries(dates).forEach(([dateStr, isoData]) => {
        const month = dateStr.slice(0, 7) // YYYY-MM
        if (!grouped[month]) grouped[month] = {}
        grouped[month][virus] = (grouped[month][virus] || 0) + Object.values(isoData).reduce((sum, v) => sum + v, 0)
      })
    })

    const result = Object.entries(grouped)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, virusData]) => ({
        month,
        ...virusData,
      }))

    setMultiVirusMonthlyData(result)
  }, [casesByDateByVirus])

  useEffect(() => {
    fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
      .then((res) => res.json())
      .then((data) => setGeoData(data))
  }, [])

  useEffect(() => {
    document.body.style.overflow = sidebarOpen ? 'hidden' : 'auto'
    return () => { document.body.style.overflow = 'auto' }
  }, [sidebarOpen])

  const totalCases = virusPieData.reduce((acc, virus) => acc + virus.value, 0)

  if (isLoading) return <LoadingScreen />

  return (
    <div className="relative flex flex-col min-h-screen bg-gray-200">


      {/* Sidebar */}
      <nav className="sticky top-0 z-[100] bg-blue-800 text-white px-6 py-4 shadow flex flex-wrap items-center justify-between gap-4">
        <div className="text-2xl font-bold">PVDH</div>

        <div className="flex flex-wrap items-center gap-2 justify-center flex-1">
          <span className="text-sm font-semibold text-white">🦠 Choix du virus :</span>
          {Object.keys(casesByDateByVirus).map((virus) => (
            <button
              key={virus}
              onClick={() => setSelectedVirus(virus)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition whitespace-nowrap ${selectedVirus === virus
                ? 'bg-white text-blue-800 shadow'
                : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
            >
              {virus}
            </button>
          ))}
        </div>

        <div className="flex gap-2 items-center">
          <Link
            to="/"
            className={`transition px-4 py-2 rounded-lg text-sm ${location.pathname === '/' ? 'bg-white text-blue-800 font-bold' : 'hover:bg-blue-700'
              }`}
          >
            📊 Dashboard
          </Link>
          <Link
            to="/admin"
            className={`transition px-4 py-2 rounded-lg text-sm ${location.pathname.startsWith('/admin') ? 'bg-white text-blue-800 font-bold' : 'hover:bg-blue-700'
              }`}
          >
            ⚙️ Administration
          </Link>
          <button
            onClick={handleLogout}
            className="transition px-4 py-2 rounded-lg text-sm bg-red-600 hover:bg-red-700 text-white"
          >
            🔓 Déconnexion
          </button>
        </div>

      </nav>



      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <main className="p-6 space-y-6">
          <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-8 relative">
            Dashboard
            <span className="block w-20 h-1 bg-blue-600 mx-auto mt-2 rounded-full"></span>
          </h1>
          <div className="bg-white rounded-lg shadow-md p-4 mb-6 space-y-6 max-w-4xl mx-auto">
            {/* 🔹 Ligne 1 : Choix du virus */}
            <div className="flex flex-wrap justify-center items-center gap-4 text-center">

            </div>

            {/* 🔹 Ligne 2 : Contrôle temporel */}
            {selectedDate && (
              <div className="flex flex-wrap justify-center items-center gap-4 text-center">
                <span className="text-sm font-semibold text-gray-700 whitespace-nowrap">📅 Date :</span>

                <input
                  type="date"
                  value={selectedDate}
                  min={virusDates[0]}
                  max={virusDates[virusDates.length - 1]}
                  onChange={(e) => {
                    const newDate = e.target.value
                    if (virusDates.includes(newDate)) setSelectedDate(newDate)
                  }}
                  className="p-2 rounded border border-gray-300 text-sm bg-white shadow-sm"
                />

                <button
                  onClick={() => {
                    const index = virusDates.indexOf(selectedDate)
                    if (index > 0) setSelectedDate(virusDates[index - 1])
                  }}
                  className="p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow transition"
                  title="Jour précédent"
                >
                  ⬅️
                </button>

                <input
                  type="range"
                  min={0}
                  max={virusDates.length - 1}
                  value={virusDates.indexOf(selectedDate)}
                  onChange={(e) => {
                    const index = parseInt(e.target.value)
                    setSelectedDate(virusDates[index])
                  }}
                  className="w-[200px] sm:w-[300px] accent-blue-600"
                />

                <button
                  onClick={() => {
                    const index = virusDates.indexOf(selectedDate)
                    if (index < virusDates.length - 1) setSelectedDate(virusDates[index + 1])
                  }}
                  className="p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow transition"
                  title="Jour suivant"
                >
                  ➡️
                </button>
              </div>
            )}
          </div>




          {/* Carte */}
          <div className="flex flex-row gap-6">
            {/* 📍 Carte interactive */}
            <div className="flex-1 card">
              <h2 className="chart-title">Carte interactive</h2>
              <WorldMap
                selectedVirus={selectedVirus}
                selectedDate={selectedDate}
                casesByDateByVirus={casesByDateByVirus}
                modalCountry={modalCountry}
                setModalCountry={setModalCountry}
              />
            </div>
          </div>
          {/* Zone graphique */}
          <div className="flex flex-row gap-4">
            <div className="flex-1 space-y-6">
              {/* Évolution temporelle */}
              <div className="card">
                <h2 className="chart-title">Évolution temporelle</h2>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={multiVirusMonthlyData} margin={{ left: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis tickFormatter={value => value >= 1_000_000 ? value / 1_000_000 + 'M' : value >= 1_000 ? value / 1_000 + 'k' : value} />
                      <Tooltip />
                      <Legend />
                      {Object.keys(casesByDateByVirus).map((virus) => (
                        <Line
                          key={virus}
                          type="monotone"
                          dataKey={virus}
                          stroke={virusColors[virus] || '#000'} // fallback noir si non défini
                          dot={false}
                        />
                      ))}

                    </LineChart>

                  </ResponsiveContainer>
                </div>
              </div>

              {/* Comparaison par continent */}
              <div className="card">
                <h2 className="chart-title">Comparaison entre les continents</h2>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={continentComparisonData} margin={{ left: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis tickFormatter={value => value >= 1_000_000 ? value / 1_000_000 + 'M' : value >= 1_000 ? value / 1_000 + 'k' : value} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="cases" fill="#82ca9d" />
                    </BarChart>

                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Camembert virus */}
            <div className="w-[400px] card flex flex-col items-center justify-center">
              <h2 className="chart-title mb-4">Répartition des cas par virus</h2>
              <ResponsiveContainer width="100%" height={480}>
                <PieChart aria-label="Camembert représentant la répartition des cas par virus" role="img">
                  <Pie
                    data={virusPieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={130}
                    activeIndex={-1}
                  >
                    {virusPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [`${Math.round((value / totalCases) * 100)}%`, name]} />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>

            </div>
          </div>
        </main>
      </div>
    </div>
  )
}