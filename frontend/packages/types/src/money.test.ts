import { describe, expect, it } from 'vitest';

import { formatAmount, formatRate, formatUgx } from './money';

describe('formatUgx', () => {
  it('writes money the way the style guide requires', () => {
    // Section 4.2: currency code, space, comma thousands, no decimals.
    expect(formatUgx(145000)).toBe('UGX 145,000');
    expect(formatUgx(2500)).toBe('UGX 2,500');
    expect(formatUgx(0)).toBe('UGX 0');
    expect(formatUgx(1234567)).toBe('UGX 1,234,567');
  });

  it('never shows decimals', () => {
    expect(formatUgx(45000)).not.toContain('.');
  });

  it('refuses a fractional amount rather than hiding it', () => {
    // A float in a money path is a bug upstream (ADR-002), not a display issue.
    expect(() => formatUgx(45000.5)).toThrow(/integer/);
  });
});

describe('formatAmount', () => {
  it('omits the prefix for tables whose header carries it', () => {
    expect(formatAmount(15000)).toBe('15,000');
  });
});

describe('formatRate', () => {
  it('reads basis points as a percentage', () => {
    expect(formatRate(1200)).toBe('12%');
    expect(formatRate(8000)).toBe('80%');
    expect(formatRate(1250)).toBe('12.50%');
  });
});
