import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemePreference = "system" | "light" | "dark";
export type NetworkMode = "testnet" | "mainnet";

export interface AppSettings {
  display: {
    theme: ThemePreference;
    compactMode: boolean;
  };
  notifications: {
    realtimeToasts: boolean;
    soundEnabled: boolean;
  };
  network: {
    mode: NetworkMode;
    liveUpdates: boolean;
  };
}

export const defaultSettings: AppSettings = {
  display: {
    theme: "system",
    compactMode: false,
  },
  notifications: {
    realtimeToasts: true,
    soundEnabled: false,
  },
  network: {
    mode: "testnet",
    liveUpdates: true,
  },
};

interface SettingsStore {
  settings: AppSettings;
  updateDisplay: (updates: Partial<AppSettings["display"]>) => void;
  updateNotifications: (updates: Partial<AppSettings["notifications"]>) => void;
  updateNetwork: (updates: Partial<AppSettings["network"]>) => void;
  resetSettings: () => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      settings: defaultSettings,
      updateDisplay: (updates) =>
        set((state) => ({
          settings: {
            ...state.settings,
            display: { ...state.settings.display, ...updates },
          },
        })),
      updateNotifications: (updates) =>
        set((state) => ({
          settings: {
            ...state.settings,
            notifications: { ...state.settings.notifications, ...updates },
          },
        })),
      updateNetwork: (updates) =>
        set((state) => ({
          settings: {
            ...state.settings,
            network: { ...state.settings.network, ...updates },
          },
        })),
      resetSettings: () => set({ settings: defaultSettings }),
    }),
    {
      name: "chainbridge-settings",
      version: 1,
    }
  )
);

export function resolveWsUrlForMode(url: string, mode: NetworkMode): string {
  if (mode === "mainnet") {
    return url.replace(/testnet/gi, "mainnet");
  }
  return url.replace(/mainnet/gi, "testnet");
}
