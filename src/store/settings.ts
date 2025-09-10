import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AppSettings } from '@/types'
import { getThemePreference, setThemePreference, applyTheme } from '@/lib/utils'

interface SettingsStore extends AppSettings {
  // Actions
  setTheme: (mode: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setAutoSave: (enabled: boolean) => void
  setSoundEnabled: (enabled: boolean) => void
  resetSettings: () => void
}

const defaultSettings: AppSettings = {
  theme: { mode: 'system' },
  sidebarCollapsed: false,
  autoSave: true,
  soundEnabled: false,
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      ...defaultSettings,

      setTheme: (mode) => {
        set((state) => ({
          theme: { ...state.theme, mode }
        }))
        setThemePreference(mode)
        applyTheme(mode)
      },

      toggleSidebar: () => {
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed
        }))
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed })
      },

      setAutoSave: (enabled) => {
        set({ autoSave: enabled })
      },

      setSoundEnabled: (enabled) => {
        set({ soundEnabled: enabled })
      },

      resetSettings: () => {
        set(defaultSettings)
        setThemePreference('system')
        applyTheme('system')
      },
    }),
    {
      name: 'whoknows-settings',
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Apply theme on hydration
          applyTheme(state.theme.mode)
        }
      },
    }
  )
)

// Initialize theme on app start
if (typeof window !== 'undefined') {
  const storedTheme = getThemePreference()
  applyTheme(storedTheme)
}