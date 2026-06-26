"""
SQLite database layer via aiosqlite.
Handles players, game sessions, and per-game scores.
"""

import aiosqlite
from pathlib import Path

DB_PATH = Path("savage_journey.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT NOT NULL,
                total_pts  INTEGER NOT NULL DEFAULT 0,
                games      INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS games (
                game_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id    INTEGER NOT NULL,
                status     TEXT NOT NULL DEFAULT 'lobby',
                started_at TEXT,
                ended_at   TEXT
            );

            CREATE TABLE IF NOT EXISTS game_players (
                game_id  INTEGER NOT NULL,
                user_id  INTEGER NOT NULL,
                username TEXT NOT NULL,
                pts      INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (game_id, user_id),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );
        """)
        await db.commit()


# ─── Player helpers ───────────────────────────────────────────────────────────

async def upsert_player(user_id: int, username: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO players (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
        """, (user_id, username))
        await db.commit()


async def get_global_leaderboard(limit: int = 10) -> list[tuple[str, int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT username, total_pts FROM players
            ORDER BY total_pts DESC
            LIMIT ?
        """, (limit,)) as cur:
            return [(row[0], row[1]) async for row in cur]


# ─── Game helpers ─────────────────────────────────────────────────────────────

async def create_game(chat_id: int) -> int:
    """Create a new game in lobby status, return game_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO games (chat_id, status) VALUES (?, 'lobby')
        """, (chat_id,))
        await db.commit()
        return cur.lastrowid  # type: ignore[return-value]


async def get_active_game(chat_id: int) -> int | None:
    """Return the game_id of an active (lobby or running) game in this chat."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT game_id FROM games
            WHERE chat_id = ? AND status IN ('lobby', 'running')
            ORDER BY game_id DESC
            LIMIT 1
        """, (chat_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def set_game_status(game_id: int, status: str) -> None:
    ts_col = "started_at" if status == "running" else "ended_at"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"""
            UPDATE games SET status = ?, {ts_col} = datetime('now')
            WHERE game_id = ?
        """, (status, game_id))
        await db.commit()


# ─── Game-player helpers ──────────────────────────────────────────────────────

async def join_game(game_id: int, user_id: int, username: str) -> bool:
    """Add player to game. Returns False if already in game."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("""
                INSERT INTO game_players (game_id, user_id, username)
                VALUES (?, ?, ?)
            """, (game_id, user_id, username))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_game_players(game_id: int) -> list[tuple[int, str]]:
    """Return list of (user_id, username) for this game."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_id, username FROM game_players WHERE game_id = ?
        """, (game_id,)) as cur:
            return [(row[0], row[1]) async for row in cur]


async def get_player_count(game_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM game_players WHERE game_id = ?
        """, (game_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def add_points(game_id: int, user_id: int, pts: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE game_players SET pts = pts + ? WHERE game_id = ? AND user_id = ?
        """, (pts, game_id, user_id))
        await db.commit()


async def get_game_scores(game_id: int) -> list[tuple[str, int]]:
    """Return (username, pts) sorted descending."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT username, pts FROM game_players
            WHERE game_id = ?
            ORDER BY pts DESC
        """, (game_id,)) as cur:
            return [(row[0], row[1]) async for row in cur]


async def finalize_scores(game_id: int) -> None:
    """Copy game points into the global players table."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_id, pts FROM game_players WHERE game_id = ?
        """, (game_id,)) as cur:
            rows = [(r[0], r[1]) async for r in cur]

        for user_id, pts in rows:
            await db.execute("""
                UPDATE players
                SET total_pts = total_pts + ?, games = games + 1
                WHERE user_id = ?
            """, (pts, user_id))
        await db.commit()
