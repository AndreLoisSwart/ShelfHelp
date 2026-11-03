import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import App from './App'
import { BASE_PATH } from './lib/base-path'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={BASE_PATH || '/'}>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
