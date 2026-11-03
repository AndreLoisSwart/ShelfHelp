import { MutationCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import { toast } from 'sonner'
import { ApiError, errorMessage } from '@/api/fetcher'
import { Toaster } from '@/components/ui/sonner'
import App from './App'
import './index.css'
import { BASE_PATH } from './lib/base-path'

const queryClient: QueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      // Retry network and server errors once; a 404 or 409 won't change on retry.
      retry: (count, error) => count < 1 && !(error instanceof ApiError && error.status < 500),
    },
  },
  mutationCache: new MutationCache({
    // The data is small, so refetch everything after any change instead of
    // tracking which queries each change affects.
    onSuccess: () => queryClient.invalidateQueries(),
    onError: (error) => toast.error(errorMessage(error)),
  }),
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={BASE_PATH || '/'}>
        <App />
      </BrowserRouter>
      <Toaster position="top-center" />
    </QueryClientProvider>
  </StrictMode>,
)
