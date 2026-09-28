/** Theme context and hook, separate from the provider component.
 *
 * Kept in its own module so `ThemeProvider.tsx` exports only a component and
 * React Fast Refresh keeps working during development.
 */
import { createContext, useContext } from 'react';
import type { ThemePreference } from '@kleim/types';

export interface ThemeContextValue {
  preference: ThemePreference;
  /** What is actually on screen once the device setting is resolved. */
  resolved: 'light' | 'dark';
  setPreference: (preference: ThemePreference) => void;
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used inside a ThemeProvider');
  return context;
}
