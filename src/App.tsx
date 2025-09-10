import { Suspense, lazy } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { useSettingsStore } from '@/store/settings'
import { cn } from '@/lib/utils'

// Lazy load heavy components
const ChatInterface = lazy(() => import('@/components/ChatInterface').then(module => ({ default: module.ChatInterface })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors, but retry on network errors
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        return failureCount < 3
      },
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
})

function AppLayout() {
  const { sidebarCollapsed } = useSettingsStore()

  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        className={cn(
          'transition-all duration-300 ease-in-out',
          sidebarCollapsed ? 'w-16' : 'w-80'
        )}
      >
        <Sidebar />
      </motion.aside>

      {/* Main Content */}
      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex-1 flex flex-col min-h-0"
      >
        <Header />
        <ErrorBoundary>
          <Suspense fallback={
            <div className="flex-1 flex items-center justify-center" role="status" aria-label="Loading chat interface">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="text-primary-600"
              >
                <Loader2 size={32} />
              </motion.div>
            </div>
          }>
            <ChatInterface />
          </Suspense>
        </ErrorBoundary>
      </motion.main>
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <div className="h-screen overflow-hidden">
          <AppLayout />
        </div>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App