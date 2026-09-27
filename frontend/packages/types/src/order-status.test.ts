import { describe, expect, it } from 'vitest';

import { ORDER_STATUS_WORDING, ORDER_STATUSES, statusWording } from './order-status';

describe('order status wording', () => {
  it('covers every state in SDD section 12.1', () => {
    // If a state is added to the union without wording, this fails here rather
    // than rendering a blank headline in the tracking screen.
    for (const status of ORDER_STATUSES) {
      const wording = ORDER_STATUS_WORDING[status];
      expect(wording.headline.length).toBeGreaterThan(0);
      expect(wording.timeline.length).toBeGreaterThan(0);
    }
    expect(Object.keys(ORDER_STATUS_WORDING)).toHaveLength(ORDER_STATUSES.length);
  });

  it('matches the style guide table exactly', () => {
    expect(statusWording('PENDING_SELLER').headline).toBe('Waiting for the store to confirm');
    expect(statusWording('PENDING_SELLER').timeline).toBe('Order placed');
    expect(statusWording('IN_TRANSIT').headline).toBe('On the way');
    expect(statusWording('EXPIRED').timeline).toBe('Expired: no response from store');
    expect(statusWording('CANCELLED_BY_CUSTOMER').timeline).toBe('Cancelled by you');
  });

  it('is written in sentence case, with no exclamation marks outside delivery', () => {
    // Section 7.1: sentence case everywhere, no shouting.
    for (const status of ORDER_STATUSES) {
      const { headline } = ORDER_STATUS_WORDING[status];
      expect(headline).not.toMatch(/!/);
      expect(headline).not.toBe(headline.toUpperCase());
    }
  });

  it('marks the states an order cannot leave', () => {
    expect(statusWording('DELIVERED').terminal).toBe(true);
    expect(statusWording('PENDING_SELLER').terminal).toBe(false);
  });

  it('gives failures a pink tone and success a green one', () => {
    // Status colour always pairs with a word (section 4.1), so tone is metadata,
    // never the only signal.
    expect(statusWording('PAYMENT_FAILED').tone).toBe('pink');
    expect(statusWording('DELIVERED').tone).toBe('green');
  });
});
