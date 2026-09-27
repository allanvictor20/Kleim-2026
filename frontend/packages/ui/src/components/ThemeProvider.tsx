/** Theme — follows the device, with an explicit override.
 *
 * Style Guide section 4.1: dark theme follows the device setting and every screen
 * is checked in both themes. The override writes `data-theme` on <html>, which is
 * the hook `tokens.css` already looks for.
 */
import { useCallback, useEffect, useState, type ReactNode } from 'react';
import type { ThemePreference } from '@kleim/types';

import { ThemeContext } from './theme-context';

function deviceTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined' || !window.matchMedia) return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({
  children,
  initial = 'system',
}: {
  children: ReactNode;
  initial?: ThemePreference;
}) {
  const [preference, setPreference] = useState<ThemePreference>(initial);
  const [device, setDevice] = useState<'light' | 'dark'>(deviceTheme);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const query = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = (event: MediaQueryListEvent) => setDevice(event.matches ? 'dark' : 'light');
    query.addEventListener('change', onChange);
    return () => query.removeEventListener('change', onChange);
  }, []);

  const resolved = preference === 'system' ? device : preference;

  useEffect(() => {
    const root = document.documentElement;
    if (preference === 'system') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', preference);
    }
    // Keep the browser chrome in step with the theme, reading the value from the
    // tokens rather than repeating a hex here (Style Guide section 4).
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      const token = resolved === 'dark' ? '--screen' : '--btn';
      const value = getComputedStyle(root).getPropertyValue(token).trim();
      if (value) meta.setAttribute('content', value);
    }
  }, [preference, resolved]);

  const update = useCallback((next: ThemePreference) => setPreference(next), []);

  return (
    <ThemeContext.Provider value={{ preference, resolved, setPreference: update }}>
      {children}
    </ThemeContext.Provider>
  );
}
