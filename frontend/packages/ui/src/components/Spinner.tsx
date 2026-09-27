/** Spinner — the loading state every screen needs (SDD Appendix B). */
export function Spinner({ label = 'Loading' }: { label?: string }) {
  return (
    <span
      role="status"
      aria-label={label}
      className="border-line border-t-link rounded-pill inline-block h-4 w-4 animate-spin border-2"
    />
  );
}
