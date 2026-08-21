"""
NaVro core config.

Kept intentionally tiny for M1 — just the DB URL. Grows as auth,
rate-limiting, etc. get added in later milestones.
"""

import os

DATABASE_URL = os.environ.get(
    "NAVRO_DATABASE_URL",
    "postgresql+psycopg://postgres:navro_dev@localhost:5432/navro",
)
