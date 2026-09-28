/** Money formatting. UI/UX Style Guide section 4.2.
 *
 * Amounts arrive from the API as integer UGX (ADR-002) and are always written
 * `UGX 145,000`: currency code, space, comma thousands, no decimals. Inside a
 * table of amounts the prefix may move to the column header, which is what
 * `formatAmount` is for.
 */

/** Integer Uganda shillings, as every money field in the API carries them. */
export type Ugx = number;

function assertInteger(amount: Ugx): void {
  if (!Number.isInteger(amount)) {
    // A fractional shilling means a float crept into a money path somewhere
    // upstream; fail loudly rather than rounding it away in the UI.
    throw new Error(`Money must be an integer number of UGX, received ${amount}`);
  }
}

/** `145000` -> `"145,000"`. For columns whose header already says UGX. */
export function formatAmount(amount: Ugx): string {
  assertInteger(amount);
  return new Intl.NumberFormat('en-UG', { maximumFractionDigits: 0 }).format(amount);
}

/** `145000` -> `"UGX 145,000"`. The default everywhere else. */
export function formatUgx(amount: Ugx): string {
  return `UGX ${formatAmount(amount)}`;
}

/** Basis points to a readable percentage: `1200` -> `"12%"`.
 *
 * Rates reach the client as integer basis points, matching `fee_configs`, so no
 * percentage is ever carried as a float.
 */
export function formatRate(basisPoints: number): string {
  const percent = basisPoints / 100;
  return `${Number.isInteger(percent) ? percent : percent.toFixed(2)}%`;
}
