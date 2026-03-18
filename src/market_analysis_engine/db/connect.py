from __future__ import annotations

import logging
import os

from market_analysis_engine.runtime.runtime import CFGDataBase
import psycopg
# import psycopg.sql

logger = logging.getLogger(__name__)


def connect(settings: CFGDataBase | None = None) -> psycopg.Connection:
    """
    Creates a psycopg connection using explicit settings or env defaults

    Params:
    - settings: optional explicit dbsettings. If omitted values are constructed
    from env variable with module defaults as fallback

    Returns:
    - psycopg.Connection: a new database connection with autocommit disabled
    """
    logger.debug("Start ..")
    s = settings or CFGDataBase(
        db_host=os.getenv("DB_HOST", "/run/postgresql"),
        db_name=os.getenv("DB_NAME", "market_analysis_engine"),
        db_user=os.getenv("DB_USER") or None,
        db_password=os.getenv("DB_PASSWORD") or None,
        db_port=int(os.getenv("DB_PORT", "5432")),
    )

    logger.debug("End ..")

    # _ensure_db_exists(s)
    return psycopg.connect(
        dbname=s.db_name,
        host=s.db_host,
        user=s.db_user,
        password=s.db_password,
        port=s.db_port,
        autocommit=False,
    )

# def _ensure_db_exists(s: CFGDataBase) -> None:
#     with psycopg.connect(
#         dbname="postgres",
#         host="/run/postgresql",
#         port=5432,
#         user=None,
#         password=None,
#         autocommit=True) as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#                 "SELECT 1 FROM pg_database WHERE datname = %s",
#                 (s.db_name,),
#             )
#             exists = cur.fetchone() is not None
#
#             if exists:
#                 return
#             cur.execute(
#                 psycopg.sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(psycopg.sql.Identifier(s.db_name))
#             )
#
#
