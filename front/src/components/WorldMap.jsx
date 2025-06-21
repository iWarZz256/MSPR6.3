import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import countries from 'i18n-iso-countries'
import frLocale from 'i18n-iso-countries/langs/fr.json'
import CountryModal from './CountryModal'


countries.registerLocale(frLocale)

const dataByVirus = {
    'COVID-19': {
        FR: 450000, DE: 120000, IT: 850000, US: 950000, CN: 5000,
        BR: 670000, IN: 300000, RU: 40000, CA: 25000, JP: 1000,
        MX: 760000, ZA: 8900, NO: 0, SE: 0, FI: 0,
    },
    'Grippe H1N1': {
        FR: 80000, DE: 60000, US: 140000, BR: 110000, IN: 50000,
    },
    'Ebola': {
        ZA: 3000, NG: 1000, CD: 20000, LR: 5000,
    },
    // ajoute d'autres virus si besoin
}

// données simulées : cas par jour et par pays pour chaque virus
export const casesByDateByVirus = {
    'COVID-19': {
        '2020-03-01': { FR: 120, IT: 300, US: 15 },
        '2020-03-02': { FR: 250, IT: 400, US: 22 },
        '2020-03-03': { FR: 300, IT: 4500000, US: 30 },
        // etc.
    },
    'Grippe H1N1': {
        '2009-05-01': { FR: 5, US: 20, MX: 300 },
        '2009-05-02': { FR: 6, US: 21, MX: 310 },
        // etc.
    }
}



function getColor(cases) {
    if (cases > 500000) return '#800026'
    if (cases > 100000) return '#BD0026'
    if (cases > 10000) return '#E31A1C'
    if (cases > 1000) return '#FC4E2A'
    if (cases > 0) return '#FD8D3C'
    return '#D3D3D3'
}

function InfoControl() {
    const map = useMap()

    useEffect(() => {
        const info = L.control({ position: 'topright' })
        info.onAdd = () => {
            const div = L.DomUtil.create('div', 'info-box bg-white p-3 rounded shadow')
            div.innerHTML = `<h4>Survoler un pays</h4>`
            return div
        }
        info.addTo(map)
        map.infoDiv = info.getContainer()
        return () => {
            info.remove()
            delete map.infoDiv
        }
    }, [map])

    return null
}

function LegendControl() {
    const map = useMap()

    useEffect(() => {
        const legend = L.control({ position: 'bottomright' })

        legend.onAdd = () => {
            const div = L.DomUtil.create('div', 'info legend bg-white p-3 rounded shadow text-sm space-y-1')
            const grades = [0, 1000, 10000, 100000, 500000]
            const labels = grades.map((grade, index) => {
                const next = grades[index + 1]
                const range = next ? `${grade} – ${next}` : `> ${grade}`
                return `
            <div class="flex items-center gap-2">
              <span style="background:${getColor(grade)}; width:16px; height:16px; display:inline-block; border:1px solid #999;"></span>
              <span>${range} cas</span>
            </div>
          `
            })
            div.innerHTML = `<strong>Légende</strong><br>${labels.join('')}`
            return div
        }

        legend.addTo(map)

        return () => {
            legend.remove()
        }
    }, [map])

    return null
}




export default function WorldMap({ selectedVirus, selectedDate, casesByDateByVirus, modalCountry, setModalCountry }) {

    const [geoData, setGeoData] = useState(null)
    const [selectedCountry, setSelectedCountry] = useState(null)
    const mapRef = useRef(null)

    useEffect(() => {
        fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
            .then((res) => res.json())
            .then((data) => setGeoData(data))
    }, [])

    useEffect(() => {
        if (!geoData || !mapRef.current || !selectedDate) return
        const map = mapRef.current
        const dayData = casesByDateByVirus[selectedVirus]?.[selectedDate] || {}

        map.eachLayer(layer => {
            if (layer.feature && layer.feature.properties) {
                const iso = (layer.feature.properties['ISO3166-1-Alpha-2'] || '').toUpperCase()
                const cases = dayData[iso] || 0
                layer.setStyle({ fillColor: getColor(cases) })
            }
        })
    }, [selectedVirus, selectedDate, geoData])

    return (
        <div className="map-wrapper h-[600px] rounded-xl overflow-hidden border shadow">
            <MapContainer
                ref={mapRef}
                center={[20, 0]}
                zoom={2}
                minZoom={2}
                maxBounds={[[-85, -180], [85, 180]]}
                maxBoundsViscosity={1.0}
                style={{ height: '100%', width: '100%', zIndex: 0 }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <InfoControl />
                <LegendControl />
                {geoData && (
                    <GeoJSON
                        data={geoData}
                        onEachFeature={(feature, layer) => {
                            const props = feature.properties
                            const isoCode = (props['ISO3166-1-Alpha-2'] || props['ISO3166-1-Alpha-3'] || '').toUpperCase()
                            const countryFR = countries.getName(isoCode, 'fr') || props.name || 'Pays inconnu'
                            const dailyData = casesByDateByVirus[selectedVirus]?.[selectedDate] || {}
                            const cases = dailyData[isoCode] || 0

                            layer.setStyle({
                                fillColor: getColor(cases),
                                weight: 1,
                                color: 'gray',
                                fillOpacity: 0.6,
                            })

                            layer.on('click', () => {
                                const bounds = layer.getBounds()
                                const iso2 = feature.properties['ISO3166-1-Alpha-2']?.toUpperCase() || ''
                                const name = countries.getName(iso2, 'fr') || feature.properties.name || 'Pays inconnu'
                                const cases = dailyData[iso2] || 0

                                setModalCountry({
                                    name,
                                    code: iso2, // Assure que ce champ est bien défini
                                    cases,
                                    bounds,
                                    geometry: feature,
                                })
                            })
                        }}
                    />
                )}
            </MapContainer>

            <CountryModal
                country={modalCountry}
                onClose={() => setModalCountry(null)}
                selectedVirus={selectedVirus}
            />

        </div>
    )
}
