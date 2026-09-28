/** Customer-facing order status wording. UI/UX Style Guide section 7.2.
 *
 * These strings map one-to-one to the SDD section 12.1 order states and are the
 * only place the words live: the timeline, order cards and notifications all
 * read from here, so a status cannot be phrased two ways in two screens.
 *
 * `ORDER_STATUS_WORDING` is typed as a total record over `OrderStatus`, so
 * adding a state to the union without adding its wording fails the build rather
 * than rendering an empty headline.
 */

export const ORDER_STATUSES = [
  'PENDING_SELLER',
  'AWAITING_PAYMENT',
  'PREPARING',
  'READY_FOR_PICKUP',
  'IN_TRANSIT',
  'DELIVERED',
  'PARTIALLY_DELIVERED',
  'RETURNED',
  'REJECTED',
  'EXPIRED',
  'PAYMENT_FAILED',
  'DELIVERY_FAILED',
  'CANCELLED_BY_CUSTOMER',
] as const;

export type OrderStatus = (typeof ORDER_STATUSES)[number];

/** How a status reads, and which status colour it pairs with.
 *
 * A status colour never stands alone (Style Guide section 4.1), so every entry
 * carries a word as well as a tone.
 */
export type StatusTone = 'neutral' | 'blue' | 'green' | 'amber' | 'pink';

export interface StatusWording {
  /** Screen headline, e.g. "On the way". */
  readonly headline: string;
  /** Timeline entry, e.g. "Picked up by rider". */
  readonly timeline: string;
  readonly tone: StatusTone;
  /** True once the order has reached a state it cannot leave. */
  readonly terminal: boolean;
}

export const ORDER_STATUS_WORDING: Readonly<Record<OrderStatus, StatusWording>> = {
  PENDING_SELLER: {
    headline: 'Waiting for the store to confirm',
    timeline: 'Order placed',
    tone: 'blue',
    terminal: false,
  },
  AWAITING_PAYMENT: {
    headline: 'Approve the payment prompt',
    timeline: 'Store confirmed, payment requested',
    tone: 'amber',
    terminal: false,
  },
  PREPARING: {
    headline: 'Store is packing your order',
    timeline: 'Store is packing',
    tone: 'blue',
    terminal: false,
  },
  READY_FOR_PICKUP: {
    headline: 'Ready, finding a rider',
    timeline: 'Ready for pickup',
    tone: 'blue',
    terminal: false,
  },
  IN_TRANSIT: {
    headline: 'On the way',
    timeline: 'Picked up by rider',
    tone: 'blue',
    terminal: false,
  },
  DELIVERED: {
    headline: 'Delivered',
    timeline: 'Delivered',
    tone: 'green',
    terminal: true,
  },
  PARTIALLY_DELIVERED: {
    headline: 'Delivered, some items returned',
    timeline: 'Delivered, some items returned',
    tone: 'green',
    terminal: true,
  },
  RETURNED: {
    headline: 'All items returned at the door',
    timeline: 'All items returned',
    tone: 'neutral',
    terminal: true,
  },
  REJECTED: {
    headline: "Store couldn't fulfil this order",
    timeline: 'Rejected by store',
    tone: 'pink',
    terminal: true,
  },
  EXPIRED: {
    headline: "Store didn't respond in time",
    timeline: 'Expired: no response from store',
    tone: 'pink',
    terminal: true,
  },
  PAYMENT_FAILED: {
    headline: "Payment wasn't completed",
    timeline: 'Payment not completed',
    tone: 'pink',
    terminal: true,
  },
  DELIVERY_FAILED: {
    headline: 'Delivery failed',
    timeline: 'Delivery failed',
    tone: 'pink',
    terminal: true,
  },
  CANCELLED_BY_CUSTOMER: {
    headline: 'Cancelled',
    timeline: 'Cancelled by you',
    tone: 'neutral',
    terminal: true,
  },
};

export function statusWording(status: OrderStatus): StatusWording {
  return ORDER_STATUS_WORDING[status];
}
