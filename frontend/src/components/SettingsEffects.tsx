"use client";

import { useEffect } from "react";
import { useTheme } from "next-themes";
import { useSettingsStore } from "@/hooks/useSettings";

export function SettingsEffects() {
  const { settings } = useSettingsStore();
  const { setTheme } = useTheme();

  useEffect(() => {
    setTheme(settings.display.theme);
  }, [setTheme, settings.display.theme]);

  useEffect(() => {
    document.body.classList.toggle("compact-ui", settings.display.compactMode);
    document.body.dataset.networkMode = settings.network.mode;

    return () => {
      document.body.classList.remove("compact-ui");
      delete document.body.dataset.networkMode;
    };
  }, [settings.display.compactMode, settings.network.mode]);

  return null;
}
