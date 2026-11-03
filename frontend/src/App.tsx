import { useEffect, useState } from 'react'
import { Link, Route, Routes } from 'react-router'
import { apiUrl, BASE_PATH } from './lib/base-path'

// Step 1 placeholder: proves routing, assets and API calls work behind Ingress.

function Home() {
  const [health, setHealth] = useState('checking…')

  useEffect(() => {
    fetch(apiUrl('/api/health'))
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then((body: { status: string; time: string }) => setHealth(`${body.status} at ${body.time}`))
      .catch((err: Error) => setHealth(`error: ${err.message}`))
  }, [])

  return (
    <>
      <h1>Shelf-help</h1>
      <p>API health: {health}</p>
      <p>Base path: {BASE_PATH || '/'}</p>
    </>
  )
}

function About() {
  return <p>Second route. Refresh this page to test deep links.</p>
}

export default function App() {
  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: 16 }}>
      <nav>
        <Link to="/">Home</Link> · <Link to="/about">About</Link> · <Link to="/nested/route">Nested</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<Home />} />
      </Routes>
    </main>
  )
}
