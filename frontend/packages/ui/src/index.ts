/** @kleim/ui — the shared design system.
 *
 * Tokens: import `@kleim/ui/tokens.css` once per app, before any component.
 * Components listed in the UI/UX Style Guide section 5 that are not here yet
 * belong to the module that first needs them (M2, M3, M5, M7); adding a component
 * the style guide does not list needs team agreement.
 */
export { AppHeader, AppShell, BottomNav, Sidebar, type NavItem } from './components/AppShell';
export { Button, type ButtonProps, type ButtonVariant } from './components/Button';
export { Chip, ChipRow, type ChipProps } from './components/Chip';
export { EmptyState, type EmptyStateProps } from './components/EmptyState';
export { ErrorBoundary, type ErrorBoundaryProps } from './components/ErrorBoundary';
export { IconButton, type IconButtonProps } from './components/IconButton';
export { Input, type InputProps } from './components/Input';
export { Skeleton, type SkeletonProps } from './components/Skeleton';
export { Spinner } from './components/Spinner';
export { Tag, type TagProps } from './components/Tag';
export { Toast, ToastStack, type ToastProps } from './components/Toast';
export { ThemeProvider } from './components/ThemeProvider';
export { useTheme, type ThemeContextValue } from './components/theme-context';
export { ComponentPreview } from './preview/ComponentPreview';
