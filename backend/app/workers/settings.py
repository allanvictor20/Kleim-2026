"""ARQ worker settings (M0). Add jobs and cron schedules as modules need them:
M5 expire_unanswered_orders, M6 reconcile_payments, M7 offer timeouts,
M8 notification delivery, M9 payout batches, M11 reliability and stock reminders."""


class WorkerSettings:
    functions: list = []
    cron_jobs: list = []
