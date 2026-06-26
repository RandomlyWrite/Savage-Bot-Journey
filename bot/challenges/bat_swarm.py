"""
Bat Swarm — Reaction Speed Challenge.
Bot posts a countdown, then a "SWAT THE BAT" button.
First player to click wins points based on reaction speed.
"""

import asyncio
import random
import time

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from narrative import texts

POINTS_MAX = 100
POINTS_MIN = 30
WAIT_MIN = 3.0   # seconds before bat appears
WAIT_MAX = 7.0
BAT_WINDOW = 8.0  # seconds to click before bat escapes
CALLBACK_PREFIX = "bat_swat:"


def make_bat_keyboard(game_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=texts.BAT_BUTTON,
            callback_data=f"{CALLBACK_PREFIX}{game_id}"
        )
    ]])


async def run(
    bot: Bot,
    chat_id: int,
    game_id: int,
    player_ids: set[int],
) -> tuple[int | None, int]:
    """
    Run a Bat Swarm round.
    Returns (winning_user_id, points_awarded) or (None, 0).
    """
    # ── intro message ────────────────────────────────────────────────────────
    await bot.send_message(
        chat_id,
        random.choice(texts.BAT_SWARM_INTRO),
        parse_mode="Markdown",
    )

    # ── random countdown before bat appears ──────────────────────────────────
    wait_msg = await bot.send_message(
        chat_id,
        random.choice(texts.BAT_SWARM_WAITING),
        parse_mode="Markdown",
    )
    delay = random.uniform(WAIT_MIN, WAIT_MAX)
    await asyncio.sleep(delay)

    # ── show the bat button ──────────────────────────────────────────────────
    bat_appeared_at = time.monotonic()
    bat_msg = await bot.send_message(
        chat_id,
        "🦇🦇🦇 *THE BATS ARE HERE!* 🦇🦇🦇",
        reply_markup=make_bat_keyboard(game_id),
        parse_mode="Markdown",
    )

    # ── wait for a click via shared future ───────────────────────────────────
    result_future: asyncio.Future[tuple[int, float]] = asyncio.get_event_loop().create_future()

    # Store future and metadata in a module-level registry so the callback
    # handler can resolve it
    _active_rounds[game_id] = {
        "future": result_future,
        "appeared_at": bat_appeared_at,
        "player_ids": player_ids,
        "false_started": set(),
    }

    try:
        winner_id, reaction_ms = await asyncio.wait_for(
            result_future,
            timeout=BAT_WINDOW,
        )
    except asyncio.TimeoutError:
        winner_id = None
        reaction_ms = 0
    finally:
        _active_rounds.pop(game_id, None)
        # Disable the button
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=bat_msg.message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    if winner_id is None:
        await bot.send_message(chat_id, texts.BAT_TOO_SLOW, parse_mode="Markdown")
        return None, 0

    # ── award points ─────────────────────────────────────────────────────────
    points = max(POINTS_MIN, POINTS_MAX - int(reaction_ms / 10))

    # find username from player list
    return winner_id, points


# ─── Active round registry ────────────────────────────────────────────────────
# Maps game_id -> round metadata dict
_active_rounds: dict[int, dict] = {}


def get_active_round(game_id: int) -> dict | None:
    return _active_rounds.get(game_id)
