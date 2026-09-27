# Kleim Operations Runbook
## 1. Purpose and how to use this runbook

This runbook tells the Kleim on-duty person exactly what to check and do when an incident happens. It covers the platform services, external providers (payments, SMS, maps) and marketplace operations (stuck orders, riders, cash). It implements the reliability and support workstreams of Implementation Plan M10 and M12 and the risks in SDD §28.

Each procedure follows the same pattern: **Signs** (how you notice), **Check** (confirm the cause), **Act** (fix or contain), **Tell** (who to inform and what to say), **After** (follow-up).

> Golden rule: protect orders and money first. When unsure, pause new orders in the affected area rather than let them fail silently.

## 2. Roles, severity and communication

### 2.1 Roles during the pilot

| Role | Who | Responsibilities |
| --- | --- | --- |
| On-duty operator | Rotating team member, 9:00–20:00 daily | Watches the exceptions queue and alerts; first responder |
| Technical lead on call | Backend lead (backup: team lead) | Fixes platform faults; approves rollbacks and data fixes |
| Finance operator | [name] | Cash remittances, payouts, refunds |
| Seller and rider contact | [name] | Calls boutiques and riders |

### 2.2 Severity levels

| Level | Definition | Examples | Response |
| --- | --- | --- | --- |
| SEV1 | Customers cannot order, or money or data is at risk | API down; database unavailable; duplicate charges; data leak | Immediately; technical lead called; pause ordering if needed |
| SEV2 | A core flow is degraded | Payment provider failing; SMS not sending; riders not receiving offers | Within 15 minutes |
| SEV3 | Single order or user affected | One stuck order; one wrong code; one seller complaint | Within 1 hour during operating hours |
| SEV4 | Cosmetic or minor | Wrong text; slow page | Next working day |

### 2.3 Communication templates

**Customer (SMS or in-app):** “Kleim: Sorry, your order #[CODE] is delayed because [reason]. We’re fixing it and will update you by [time].”

**Seller:** “Kleim: Hello [name], order #[CODE]: [what happened]. Please [action]. Call [support number] if you need help.”

**Team (chat):** “[SEV#] [short title]. Impact: [who/what]. Started: [time]. Owner: [name]. Next update: [time].”

Post a team update every 30 minutes for SEV1 and every hour for SEV2 until resolved.

## 3. Daily and weekly routines

### 3.1 Opening checklist (9:00)

- [ ] Health endpoints green: `/health/live`, `/health/ready` on production.
- [ ] Sentry: no new unresolved errors since yesterday.
- [ ] Worker queue length normal (under 100 jobs) and no failed jobs overnight.
- [ ] Exceptions queue empty or assigned.
- [ ] Riders online for the morning; at least [N] per active zone.
- [ ] Yesterday’s COD cash reconciled or followed up.
- [ ] SMS balance above the alert threshold.

### 3.2 Closing checklist (20:00)

- [ ] No orders in PENDING_SELLER, AWAITING_PAYMENT, PREPARING or READY_FOR_PICKUP without an owner.
- [ ] All in-transit deliveries completed or handed to tomorrow with the customer informed.
- [ ] Riders’ cash remittances recorded; overdue list noted.
- [ ] Daily pilot metrics captured (Implementation Plan M12).

### 3.3 Weekly routines

| Day | Task | Owner |
| --- | --- | --- |
| Monday | Generate and review payout batch; mark paid after transfer | Finance |
| Monday | Review seller reliability scores; call sellers below 80 | Seller contact |
| Wednesday | Restore test of last night’s backup to staging (monthly) | Technical lead |
| Friday | Review incidents and update this runbook | Team lead |

## 4. Platform incidents

### 4.1 API down or very slow (SEV1)

**Signs:** uptime alert; apps show errors; health endpoint fails or p95 above 2 seconds.

**Check:**

1. Hosting dashboard: are API containers running? Recent deploy?
2. Sentry and logs: errors starting at a specific time?
3. Database connections: connection pool exhausted? Long-running queries (`pg_stat_activity`)?
4. Redis reachable?

**Act:**

- If a deploy happened in the last hour, **roll back** to the previous release (§4.4).
- If the database is overloaded, cancel the offending query and scale the API down temporarily to reduce connections.
- If the host is down, fail over or redeploy to the same platform in another region if available.

**Tell:** Team immediately. If over 15 minutes, post a banner in the apps (“We’re having a problem placing orders. Please try again shortly.”).

**After:** incident note within 24 hours: cause, timeline, fix, prevention.

### 4.2 Database unavailable or data damaged (SEV1)

**Act:**

1. Stop the worker to prevent jobs writing partial data.
2. Put the API in read-only maintenance mode (environment flag `MAINTENANCE_MODE=true`) so apps show a clear message.
3. If data is damaged, restore the latest backup to a **new** database, verify row counts and the ledger check query, then switch the connection string. Never restore over the damaged database.
4. Reconcile orders and payments created between the backup time and the incident using provider dashboards and SMS logs.

**Tell:** team lead and supervisor; affected customers and sellers once scope is known.

### 4.3 Background worker stopped (SEV2)

**Signs:** seller countdowns reach zero but orders do not expire; offers not sent; SMS queued but not delivered.

**Check:** worker container status; Redis reachable; failed jobs list.

**Act:** restart the worker. Expiry and offer jobs are idempotent and catch up automatically. Check the exceptions queue afterwards for orders that expired late and contact affected sellers.

### 4.4 Bad deployment and rollback

1. Identify the previous good release tag.
2. Redeploy that tag from the hosting dashboard or `git revert` and merge to trigger CI.
3. If the release included a migration, check it is backward compatible. Rollbacks never run `alembic downgrade` in production without the technical lead; prefer a forward fix.
4. Confirm health checks and a test order on staging data.

## 5. External provider incidents

### 5.1 Mobile-money payments failing (SEV2)

**Signs:** many orders in AWAITING_PAYMENT or PAYMENT_FAILED; webhook errors in logs; provider status page shows issues.

**Check:** provider dashboard and status page; webhook signature errors (secret rotated?); outbound calls timing out.

**Act:**

1. If the provider is down, switch the admin setting **Mobile money available** to off. Checkout then offers cash on delivery only, with a message.
2. For orders already waiting, contact customers to offer cash on delivery; the operator can switch the order’s payment method from the order page (audited).
3. When the provider recovers, run the payment reconciliation job manually and compare with the provider’s transaction list.

**Never** mark an order paid without a provider reference.

### 5.2 Duplicate or wrong charge reported (SEV1 if several)

1. Find the order and all `payments` rows; compare with the provider dashboard by reference.
2. If a duplicate is confirmed, create a refund record, process it in the provider dashboard, record the reference and tell the customer the expected time.
3. If several customers are affected, pause mobile money (§5.1) until the cause is found.

### 5.3 SMS not delivering (SEV2)

**Signs:** OTP complaints; sellers missing new-order alerts; provider delivery reports failing; low SMS balance alert.

**Act:**

1. Top up the SMS balance if low.
2. If the provider is down, sellers will not receive alerts: the operator calls each seller with a pending order from the exceptions queue.
3. Customers who cannot log in can be helped only after identity is confirmed by phone call; never read an OTP to anyone.

### 5.4 Maps or geocoding failing (SEV3)

Checkout falls back to straight-line distance × 1.3 automatically. If pin search fails, customers can still drop pins manually. Check API key quotas and billing.

## 6. Marketplace operations

### 6.1 Seller not responding

**Signs:** order near its deadline in PENDING_SELLER; exceptions queue item.

**Act:** call the seller at the 5-minute mark. If they confirm stock, ask them to accept in the app. If unreachable, let the order expire; the customer is automatically offered similar items. Repeated non-response lowers reliability; after 3 in a week, the seller contact calls to agree on a fix or temporarily hides the store.

### 6.2 No rider found (SEV3, SEV2 if widespread)

**Signs:** exceptions queue “no rider after 5 offers or 10 minutes”.

**Act:**

1. Check online riders in the zone; call riders who are nearby but offline.
2. Assign manually from the ops console once a rider agrees.
3. If no rider within 20 minutes, tell the customer the new time or offer cancellation with no charge.
4. If this happens often in a zone, reduce that zone’s delivery radius or pause “Arrives today” there until more riders join.

### 6.3 Rider cannot reach the customer

The rider marks the delivery failed after 3 calls over 10 minutes. The operator tries the customer once more, then either arranges a reattempt the same day (if the customer answers) or instructs the rider to return items to the store with the return code. Delivery fee handling follows the failed-delivery policy.

### 6.4 Wrong or lost handover code

1. Confirm identity by calling the person from the number on the order.
2. Reissue the code from the ops console (audited) and send it by SMS to the correct party.
3. If a code is locked after 5 wrong attempts, check for possible fraud before reissuing.

### 6.5 Customer dispute (wrong item, damaged, not received)

1. Open or find the support ticket; check order history, handover codes, timestamps and rider location trail.
2. Call the customer, then the seller and rider if needed.
3. Decide within 24 hours: refund, replacement, or no action with explanation. Record the resolution and any refund in the ticket.

### 6.6 Rider cash not remitted (SEV3)

**Signs:** exceptions queue “COD cash overdue” or rider blocked by cash limit.

**Act:** call the rider; agree remittance by MoMo to the platform number or at the office the same day. Finance records the remittance with the transaction reference. Unremitted cash after 3 days: suspend the rider’s COD jobs and escalate to the team lead.

### 6.7 Suspicious activity

Examples: many new accounts from one device, repeated failed codes, orders with the same address and different names, a seller listing obviously counterfeit or prohibited items.

Act: suspend the account or product (audited, with reason), preserve logs, inform the team lead. Do not contact suspected fraudsters with details of how they were detected.

## 7. Security and data incidents

### 7.1 Suspected data leak or account compromise (SEV1)

1. Contain: revoke sessions (`POST /admin/users/{id}/revoke-sessions`), rotate exposed secrets (JWT secret, provider keys, database password), disable affected accounts.
2. Preserve evidence: export logs and audit entries for the period before they rotate.
3. Assess: what data, whose, how many, since when.
4. Notify: team lead and supervisor immediately. Under the Data Protection and Privacy Act 2019, a breach must be reported to the Personal Data Protection Office and affected people informed; confirm current requirements and timelines with a legal adviser.
5. Fix the cause and write an incident report.

### 7.2 Secret committed to the repository

Rotate the secret immediately (removing it from Git history is not enough), then purge history, check logs for misuse and add the pattern to the secret scanner.

## 8. Useful queries and admin actions

All data fixes in production are done through the admin console where possible. Direct SQL requires the technical lead’s approval and an audit note.

Orders stuck in a state for more than 30 minutes:

```
SELECT code, status, updated_at FROM orders
 WHERE status IN ('PENDING_SELLER','AWAITING_PAYMENT','PREPARING','READY_FOR_PICKUP','IN_TRANSIT')
   AND updated_at < now() - interval '30 minutes'
 ORDER BY updated_at;
```

Reserved stock that no active order explains (should return no rows):

```
SELECT v.id, v.reserved_quantity, COALESCE(SUM(oi.quantity),0) AS active_reserved
  FROM product_variants v
  LEFT JOIN order_items oi ON oi.variant_id = v.id
  LEFT JOIN orders o ON o.id = oi.order_id
   AND o.status IN ('PENDING_SELLER','AWAITING_PAYMENT','CONFIRMED','PREPARING','READY_FOR_PICKUP')
 GROUP BY v.id HAVING v.reserved_quantity <> COALESCE(SUM(oi.quantity),0);
```

Unbalanced ledger transactions (must return no rows):

```
SELECT transaction_id, SUM(amount) FROM ledger_entries GROUP BY transaction_id HAVING SUM(amount) <> 0;
```

| Admin action | Where | Audited |
| --- | --- | --- |
| Pause ordering in a zone | Admin › Settings › Zones | Yes |
| Turn mobile money off/on | Admin › Settings › Payments | Yes |
| Reassign rider | Ops › Order › Delivery | Yes |
| Cancel order with reason | Ops › Order | Yes |
| Reissue handover code | Ops › Delivery | Yes |
| Suspend seller, rider or product | Admin | Yes |
| Record refund or remittance | Finance | Yes |

## 9. Contacts

| Contact | Number / link |
| --- | --- |
| Technical lead on call | [phone] |
| Team lead | [phone] |
| Payment provider support | [link / phone] |
| SMS provider support | [link / phone] |
| Hosting provider status page | [link] |
| Supervisor | [phone / email] |

## 10. Incident report template

| Field | Content |
| --- | --- |
| Title and severity | |
| Start and end time | |
| Impact | Orders, customers, sellers, money affected |
| Timeline | Key events with times |
| Root cause | |
| What went well / badly | |
| Actions | Owner and due date for each |
