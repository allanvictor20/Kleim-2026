/** Shared UI state types not covered by the generated API client. */

/** Every screen handles all four (SDD Appendix B, CONTRIBUTING.md section 5). */
export type LoadState = 'loading' | 'empty' | 'error' | 'ready';

/** Colour tones shared by tags, badges and status rows. */
export type Tone = 'neutral' | 'blue' | 'green' | 'amber' | 'pink';

/** Theme follows the device unless a person overrides it. */
export type ThemePreference = 'system' | 'light' | 'dark';

/** The roles the API issues, matching the `Role` schema in openapi.yaml. */
export const USER_ROLES = ['customer', 'seller', 'rider', 'support', 'finance', 'admin'] as const;
export type UserRole = (typeof USER_ROLES)[number];

export const ROLE_STATUSES = ['pending', 'approved', 'suspended'] as const;
export type RoleStatus = (typeof ROLE_STATUSES)[number];

/** Occasion vocabulary is fixed (SDD REC-02) and served by `GET /catalog/tags`;
 * this is the local mirror used for chip ordering and labels. */
export const OCCASIONS = [
  'university',
  'wedding',
  'kwanjula',
  'party',
  'church',
  'interview',
  'date',
  'graduation',
  'casual',
] as const;
export type Occasion = (typeof OCCASIONS)[number];

/** Labels use the words customers use (Style Guide section 7.4). */
export const OCCASION_LABELS: Readonly<Record<Occasion, string>> = {
  university: 'University / campus',
  wedding: 'Wedding',
  kwanjula: 'Introduction / Kwanjula',
  party: 'Party',
  church: 'Church',
  interview: 'Interview',
  date: 'Date',
  graduation: 'Graduation',
  casual: 'Casual',
};
