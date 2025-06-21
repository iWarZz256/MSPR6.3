import React, { useState, useEffect } from 'react'
import logo from '../assets/PVDH.png'

const messages = [
  "Chargement des données de santé...",
  "Connexion sécurisée à PVDH..."
]

export default function LoadingScreen() {
  const [messageIndex, setMessageIndex] = useState(0)

  useEffect(() => {
    // Changement de message toutes les 2 secondes
    const interval = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % messages.length)
    }, 2000)

    // Simulation d’un chargement (peut être connecté à un vrai state `isLoading`)
    const timer = setTimeout(() => {
      console.log("Chargement terminé !")
    }, 5000)

    return () => {
      clearInterval(interval)
      clearTimeout(timer)
    }
  }, [])
  

  return (
    <div className="relative flex flex-col items-center justify-center h-screen bg-gradient-to-br from-white via-blue-50 to-blue-100 overflow-hidden">

      {/* Background décoratif médical style "molécules" */}
      <div className="absolute inset-0 opacity-10 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/connected.png')] bg-repeat" />

      {/* Logo */}
      <img
        src={logo}
        alt="Logo"
        className="w-36 mb-8 animate-pulse z-10"
      />

      {/* Spinner */}
      <div className="relative w-16 h-16 mb-6 z-10">
        <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
        <div className="absolute inset-2 rounded-full bg-transparent"></div>
      </div>

      {/* Message qui change */}
      <p className="text-gray-600 text-sm text-center z-10 animate-fade-in-out">
        {messages[messageIndex]}
      </p>
    </div>
  )
}
