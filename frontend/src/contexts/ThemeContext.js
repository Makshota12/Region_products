import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

export const THEMES = [
  { id: 'red', label: 'Красная', emoji: '🟥' },
  { id: 'purple', label: 'Фиолетовая', emoji: '🟪' },
  { id: 'yellow', label: 'Жёлтая', emoji: '🟨' },
];

const DEFAULT_THEME = 'red';
const STORAGE_KEY = 'app-theme';

const ThemeContext = createContext({
  theme: DEFAULT_THEME,
  setTheme: () => {},
  themes: THEMES,
});

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    if (typeof window === 'undefined') return DEFAULT_THEME;
    const saved = window.localStorage.getItem(STORAGE_KEY);
    return THEMES.some((t) => t.id === saved) ? saved : DEFAULT_THEME;
  });

  useEffect(() => {
    applyTheme(theme);
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // localStorage недоступен — игнорируем
    }
  }, [theme]);

  const setTheme = useCallback((next) => {
    if (THEMES.some((t) => t.id === next)) {
      setThemeState(next);
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
