import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import {
    ResponsiveContainer, LineChart, Line,
    XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts'
import { useEffect, useRef, useState } from 'react'
import * as turf from '@turf/turf'

//Fonction utilitaire pour vérifier si les bounds sont valides pour Leaflet
function isValidLeafletBounds(bounds) {
    return (
        Array.isArray(bounds) &&
        bounds.length === 4 &&
        bounds.every(val => typeof val === 'number' && !isNaN(val))
    )
}
// Fonction utilitaire pour obtenir les bounds du plus grand polygone
function getLargestPolygonBounds(geoJson) {
    let largest = null
    let maxArea = 0

    const features = geoJson.type === 'FeatureCollection'
        ? geoJson.features
        : [geoJson]

    features.forEach(feature => {
        const geometry = feature.geometry

        if (geometry.type === 'MultiPolygon') {
            geometry.coordinates.forEach(coords => {
                const polygon = turf.polygon(coords)
                const area = turf.area(polygon)
                if (area > maxArea) {
                    maxArea = area
                    largest = polygon
                }
            })
        } else if (geometry.type === 'Polygon') {
            const polygon = turf.polygon(geometry.coordinates)
            const area = turf.area(polygon)
            if (area > maxArea) {
                maxArea = area
                largest = polygon
            }
        }
    })

    return largest ? turf.bbox(largest) : null
}
// Composant principal pour afficher les détails d'un pays dans un modal
export default function CountryModal({ country, onClose, selectedVirus }) {

    const mapRef = useRef(null)
    const [historicalData, setHistoricalData] = useState([])
    const current = historicalData.at(-1)?.cases || 0
    const previous = historicalData.at(-2)?.cases || 0
    const growthRate = previous ? (current - previous) / previous : 0
    const projected = Math.round(current * (1 +growthRate))
    const projectionTrend = growthRate > 0 ? 'hausse' : growthRate < 0 ? 'baisse' : 'stable'

    const bounds = country?.geometry ? getLargestPolygonBounds(country.geometry) : null
    const [population, setPopulation] = useState(null)
    const [predictionData, setPredictionData] = useState([]);
    const [tauxMortalite, setTauxMortalite] = useState(null);
    const [tauxTransmission, setTauxTransmission] = useState(null);
    const [selectedDataType, setSelectedDataType] = useState('classic'); // State to track selected data type


   useEffect(() => {
    console.log("🔍 useEffect prédiction déclenché", { code: country?.code, virus: selectedVirus });
 
    if (!country?.code || !selectedVirus) {
      
      return;
    }
    console.log("country.code", country.code)
    const paysIso = country.code.toLowerCase();
    fetch(`${API_URL}/predict/mortalite/${encodeURIComponent(selectedVirus)}/${paysIso}`)
            .then(data => {
            if (!data.ok) throw new Error(`Erreur ${data.status}`);
            return data.json();
            }).then(data => {
                const taux = data.map(entry => ({
                    date: entry.date,
                    tauxMortalite: entry.taux ? Number(entry.taux) : 0 // Default to 0 if invalid
                }));
                console.log("✅ Taux de mortalité récupéré :", taux);
                setTauxMortalite(taux);
            })
            .catch(err => {
                console.error("❌ Échec récupération taux de mortalité :", err);
                setTauxMortalite([]);
            });

    fetch(`${API_URL}/predict/transmission/${encodeURIComponent(selectedVirus)}/${paysIso}`)
      .then(res => {
        if (!res.ok) throw new Error(`Erreur ${res.status}`);
        return res.json();
      }
        )
        .then(data => {
        const taux = data.map(entry => ({
          date: entry.date,
            tauxTransmission: entry.taux ? Number(entry.taux) : 0 // Default to 0 if invalid
        }));
        console.log("✅ Taux de transmission récupéré :", taux);

        setTauxTransmission(taux);
      })

    const url = `${API_URL}/predict/${encodeURIComponent(selectedVirus)}/${paysIso}`;
    console.log("➡️ URL prédiction :", url);
    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`Erreur ${res.status}`);
        return res.json();
      })
      .then(data => {
    console.log(" raw prediction API response:", data);
  // data est directement un tableau de { date, predit }
  const formatted = data.map(entry => ({
    date: entry.date,
    predit: Number(entry.predit)
  }));



  console.log(" formatted predictionData:", formatted);
  setPredictionData(formatted);
})
      .catch(err => {
        console.error("❌ Échec récupération prédiction :", err);
        setPredictionData([]);
      });
  }, [country?.code, selectedVirus]);
    
  
    useEffect(() => {
        if (!country?.code) return

        fetch(`${API_URL}/suivis/pays/${country.code}?pandemie=${encodeURIComponent(selectedVirus)}`)

            .then(res => res.json())
            .then(data => {
                const formatted = data.map(entry => ({
                    date: entry.date_jour,             // YYYY-MM-DD
                    cases: Number(entry.total_cas),
                    deaths: Number(entry.total_mort),
                    recovered: Number(entry.guerison),

                }))
                setHistoricalData(formatted)
            })

            .catch(() => setHistoricalData([]))
    }, [country])

    useEffect(() => {
        if (!country?.code) return
        fetch(`https://restcountries.com/v3.1/alpha/${country.code}`)
            .then(res => res.json())
            .then(data => {
                const pop = data?.[0]?.population || null
                setPopulation(pop)
            })
            .catch(() => setPopulation(null))
    }, [country])
    useEffect(() => {
        // 🔄 Force recalcul de la taille de la carte après chargement du pays
        if (mapRef.current) {
            setTimeout(() => {
                mapRef.current.invalidateSize()
            }, 100)
        }
    }, [country])

    const [chartData, setChartData] = useState([]);


useEffect(() => {
  const table = {};

  // Map historical data
  historicalData.forEach(({ date, cases, deaths, recovered }) => {
    table[date] = {
      ...table[date],
      date,
      cases,
      deaths,
      recovered,
    };
  });

  // Map prediction data
  predictionData.forEach(({ date, predit }) => {
    table[date] = {
      ...table[date],
      date,
      predit,
    };
  });

  // Map tauxMortalite
  tauxMortalite?.forEach(({ date, tauxMortalite }) => {
    table[date] = {
      ...table[date],
      date,
      tauxMortalite,
    };
  });

  // Map tauxTransmission
  tauxTransmission?.forEach(({ date, tauxTransmission }) => {
    table[date] = {
      ...table[date],
      date,
      tauxTransmission,
    };
  });

  // Merge and sort data
  const merged = Object.values(table).sort((a, b) => new Date(a.date) - new Date(b.date));
  setChartData(merged);
}, [historicalData, predictionData, tauxMortalite, tauxTransmission]);


    if (!country || !country.bounds || !country.geometry) return null
    //console.log("VALEUR CHARDATA",chartData);
    return (
        <div className="fixed inset-0 z-[9999] bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white w-[90vw] h-[80vh] rounded-xl shadow-lg overflow-hidden flex flex-row">

                {/* Gauche : carte fixée */}
                <div className="w-1/2 h-full relative">
                    {isValidLeafletBounds(bounds) && (
                        <MapContainer
                            key={country.code}
                            bounds={[
                                [bounds[1], bounds[0]],
                                [bounds[3], bounds[2]]
                            ]}
                            whenCreated={(mapInstance) => {
                                mapRef.current = mapInstance
                                setTimeout(() => {
                                    mapInstance.invalidateSize()
                                }, 100)
                            }}
                            style={{ height: '100%', width: '100%' }}
                            dragging={false}
                            scrollWheelZoom={false}
                            doubleClickZoom={false}
                            boxZoom={false}
                            zoomControl={false}
                            attributionControl={false}
                        >
                            <TileLayer
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                attribution=""
                            />
                            {country.geometry && (
                                <GeoJSON
                                    data={country.geometry}
                                    style={{ fillColor: '#3182ce', weight: 1, color: '#2c5282', fillOpacity: 0.5 }}
                                />
                            )}
                        </MapContainer>
                    )}
                </div>
                {/* Droite : stats */}
                <div className="w-1/2 p-6 flex flex-col overflow-y-auto">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-4">
                            <img
                                src={`https://flagcdn.com/w40/${country.code.toLowerCase()}.png`}
                                alt={`Drapeau de ${country.name}`}
                                className="w-6 h-4 rounded shadow"
                            />
                            <h2 className="text-2xl font-bold">{country.name}</h2>
                            <div className="bg-blue-100 text-blue-800 font-semibold px-3 py-1 rounded shadow text-sm uppercase">
                                {country.code}
                            </div>
                        </div>
                        {population && (
                            <div className="text-sm text-gray-600 ml-1 mt-1">
                                Population : <span className="font-semibold">{population.toLocaleString()} habitants</span>
                            </div>
                        )}
                        <button
                            onClick={onClose}
                            className="text-white bg-red-500 hover:bg-red-600 px-4 py-2 rounded"
                        >
                            Fermer
                        </button>
                    </div>
                    <div className="flex-1">
                        <h3 className="text-xl font-semibold mb-4 text-gray-800">Évolution épidémiologique</h3>
                        <div className="h-72 bg-gray-50 rounded-xl shadow-inner p-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={selectedDataType === 'classic' ? chartData.map(({ date, cases, deaths, recovered, predit }) => ({ date, cases, deaths, recovered, predit })) : chartData.map(({ date, tauxMortalite, tauxTransmission }) => ({ date, tauxMortalite, tauxTransmission }))}>
                                    <defs>
                                        <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorDeaths" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#e53e3e" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#e53e3e" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorRecovered" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#38a169" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#38a169" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>

                                    <XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={str => {const [year, month] = str.split('-');
                                     return `${month}-${year}`;  }}/>
                                    <YAxis tick={{ fontSize: 12 }} />
                                    <Tooltip
                                    contentStyle={{ backgroundColor: '#fff', borderRadius: 8, border: '1px solid #eee' }}
                                    labelFormatter={d => `Date : ${d}`}
                                    formatter={(value, name) => [value.toLocaleString(), name]}
                                     />
                                    <Legend 
                                        verticalAlign="top" 
                                        iconType="circle" 
                                        height={36} 
                                        payload={selectedDataType === 'classic' 
                                            ? [
                                                { value: 'Cas', type: 'line', color: '#8884d8' },
                                                { value: 'Morts', type: 'line', color: '#e53e3e' },
                                                { value: 'Guérisons', type: 'line', color: '#38a169' },
                                                { value: 'Prédiction', type: 'line', color: '#fa9965' }
                                              ]
                                            : [
                                                { value: 'Taux Mortalité', type: 'line', color: '#8884d8' },
                                                { value: 'Taux Transmission', type: 'line', color: '#e53e3e' }

                                              ]
                                        }
                                    />
                                    <CartesianGrid strokeDasharray="2 4" stroke="#f0f0f0" />
                                    {selectedDataType === 'classic' ? (
                                        <>
                                            <Line
                                                type="monotone"
                                                dataKey="cases"
                                                name="Cas"
                                                stroke="#8884d8"
                                                strokeWidth={2.5}
                                                dot={false}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="deaths"
                                                name="Morts"
                                                stroke="#e53e3e"
                                                strokeWidth={2.5}
                                                dot={false}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="recovered"
                                                name="Guérisons"
                                                stroke="#38a169"
                                                strokeWidth={2.5}
                                                dot={false}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="predit"
                                                name="Prédiction"
                                                stroke="#fa9965"
                                                strokeWidth={2.5}
                                                dot={false}
                                                isAnimationActive={false}
                                            />
                                        </>
                                    ) : (
                                        <>
                                            <Line
                                                type="monotone"
                                                dataKey="tauxMortalite"
                                                name="Taux Mortalité"
                                                stroke="#8884d8"
                                                strokeWidth={2.5}
                                                dot={false}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="tauxTransmission"
                                                name="Taux Transmission"
                                                stroke="#e53e3e"
                                                strokeWidth={2.5}
                                                dot={false}
                                            />
                                        </>
                                    )}
                                    <YAxis yAxisId={1} tick={{ fontSize: 12 }} />
                                   
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="mt-3 flex flex-row gap-4">
                            <div className="w-full bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4 shadow">
                                <h4 className="text-md font-semibold text-blue-800 mb-2">📈 Projection des cas</h4>
                                <p className="text-sm text-blue-900 leading-relaxed">
                                    Si la tendance actuelle se poursuit, le nombre de cas pourrait atteindre environ
                                    <span className="font-semibold text-blue-700"> {projected.toLocaleString()} cas</span> d’ici l’année prochaine,
                                    soit une <span className="font-semibold">
                                        {projectionTrend === 'hausse' && 'hausse'}
                                        {projectionTrend === 'baisse' && 'baisse'}
                                        {projectionTrend === 'stable' && 'stagnation'}
                                    </span> par rapport à l’année précédente.
                                </p>
                            </div>
                        </div>

                        {/* Add styling to radio buttons */}
<div className="flex justify-center gap-4 mt-3">
  <button
    onClick={() => setSelectedDataType('classic')}
    className={`px-4 py-2 rounded-lg font-medium transition duration-200 ease-in-out ${selectedDataType === 'classic' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
  >
    Données classiques
  </button>
  <button
    onClick={() => setSelectedDataType('mortality')}
    className={`px-4 py-2 rounded-lg font-medium transition duration-200 ease-in-out ${selectedDataType === 'mortality' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
  >
    Taux de mortalité <br></br>et de transmission
  </button>
</div>
                    </div>
                </div>
            </div>
        </div>
    )
}
