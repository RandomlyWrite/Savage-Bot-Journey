"""
Slash command handlers: /start /join /begin /score /end /help
"""

import asyncio
import logging

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from db import database as db
from narrative import texts
from handlers import peak_engine

logger = logging.getLogger(__name__)
router = Router()

# Tracks running game tasks per chat: chat_id -> asyncio.Task
_running_games: dict[int, asyncio.Task] = {}


def _is_group(message: Message) -> bool:
    return message.chat.type in ("group", "supergroup")


def _get_username(message: Message) -> str:
    user = message.from_user
    if not user:
        return "Unknown"
    return user.first_name or user.username or f"User{user.id}"


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(texts.INTRO, parse_mode="Markdown")


# ─── /help ────────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(texts.HELP_TEXT, parse_mode="Markdown")


# ─── /join ────────────────────────────────────────────────────────────────────

@router.message(Command("join"))
async def cmd_join(message: Message) -> None:
    if not _is_group(message):
        await message.answer(texts.NOT_IN_GROUP, parse_mode="Markdown")
        return

    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return

    username = _get_username(message)
    await db.upsert_player(user.id, username)

    game_id = await db.get_active_game(chat_id)

    if game_id is None:
        # Open a new lobby
        game_id = await db.create_game(chat_id)
        joined = await db.join_game(game_id, user.id, username)
        count = await db.get_player_count(game_id)
        await message.answer(texts.LOBBY_OPEN, parse_mode="Markdown")
        await message.answer(
            texts.player_joined(username, count), parse_mode="Markdown"
        )
        return

    # Check if game is already running
    if chat_id in _running_games and not _running_games[chat_id].done():
        await message.answer(texts.GAME_ALREADY_RUNNING, parse_mode="Markdown")
        return

    joined = await db.join_game(game_id, user.id, username)
    count = await db.get_player_count(game_id)

    if joined:
        await message.answer(texts.player_joined(username, count), parse_mode="Markdown")
    else:
        await message.answer(texts.already_joined(username), parse_mode="Markdown")


# ─── /begin ───────────────────────────────────────────────────────────────────

@router.message(Command("begin"))
async def cmd_begin(message: Message, bot: Bot) -> None:
    if not _is_group(message):
        await message.answer(texts.NOT_IN_GROUP, parse_mode="Markdown")
        return

    chat_id = message.chat.id

    # Check for ongoing game
    if chat_id in _running_games and not _running_games[chat_id].done():
        await message.answer(texts.GAME_ALREADY_RUNNING, parse_mode="Markdown")
        return

    game_id = await db.get_active_game(chat_id)
    if game_id is None:
        await message.answer(
            "⚠️ No lobby is open. Use /join to start one.",
            parse_mode="Markdown",
        )
        return

    count = await db.get_player_count(game_id)
    if count < 2:
        await message.answer(texts.NOT_ENOUGH_PLAYERS, parse_mode="Markdown")
        return

    # Launch game as background task
    task = asyncio.create_task(
        peak_engine.run_game(bot=bot, chat_id=chat_id, game_id=game_id)
    )
    _running_games[chat_id] = task

    def _on_done(t: asyncio.Task) -> None:
        _running_games.pop(chat_id, None)
        if t.exception():
            logger.exception("Game task failed", exc_info=t.exception())

    task.add_done_callback(_on_done)


# ─── /score ───────────────────────────────────────────────────────────────────

@router.message(Command("score"))
async def cmd_score(message: Message) -> None:
    if not _is_group(message):
        # In DM: show global leaderboard
        scores = await db.get_global_leaderboard()
        await message.answer(
            texts.scoreboard(scores, title="ALL-TIME LEADERBOARD"),
            parse_mode="Markdown",
        )
        return

    chat_id = message.chat.id
    game_id = await db.get_active_game(chat_id)

    if game_id is None:
        # Fall back to global
        scores = await db.get_global_leaderboard()
        await message.answer(
            texts.scoreboard(scores, title="ALL-TIME LEADERBOARD"),
            parse_mode="Markdown",
        )
        return

    scores = await db.get_game_scores(game_id)
    await message.answer(
        texts.scoreboard(scores, title="CURRENT STANDINGS"),
        parse_mode="Markdown",
    )


# ─── /end ─────────────────────────────────────────────────────────────────────

@router.message(Command("end"))
async def cmd_end(message: Message) -> None:
    if not _is_group(message):
        await message.answer(texts.NOT_IN_GROUP, parse_mode="Markdown")
        return

    chat_id = message.chat.id
    task = _running_games.get(chat_id)

    if task and not task.done():
        task.cancel()
        _running_games.pop(chat_id, None)

    game_id = await db.get_active_game(chat_id)
    if game_id:
        await db.set_game_status(game_id, "aborted")

    await message.answer(texts.GAME_ABORTED, parse_mode="Markdown")
