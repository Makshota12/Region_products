import React, { useEffect, useRef, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';

export default function ThemeSwitcher() {
  const { theme, setTheme, themes } = useTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const current = themes.find((t) => t.id === theme) || themes[0];

  return (
    <div className="theme-switcher" ref={ref}>
      <button
        type="button"
        className="theme-switcher-trigger"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        title="Сменить тему оформления"
      >
        <span className="theme-switcher-emoji" aria-hidden="true">{current.emoji}</span>
        <span className="theme-switcher-label">{current.label}</span>
        <span className="theme-switcher-arrow" aria-hidden="true">▾</span>
      </button>

      {open && (
        <ul className="theme-switcher-menu" role="listbox">
          {themes.map((t) => (
            <li key={t.id}>
              <button
                type="button"
                role="option"
                aria-selected={t.id === theme}
                className={`theme-switcher-option ${t.id === theme ? 'is-active' : ''}`}
                onClick={() => {
                  setTheme(t.id);
                  setOpen(false);
                }}
              >
                <span className="theme-switcher-emoji" aria-hidden="true">{t.emoji}</span>
                <span className="theme-switcher-option-label">{t.label}</span>
                {t.id === theme && <span className="theme-switcher-check" aria-hidden="true">✓</span>}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
