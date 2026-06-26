"""
Inline keyboard callback router.
Handles clicks from all active challenge rounds.
"""

import time
import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from challenges import bat_swarm, attorneys_advice, lizard_loyalty
from narrative import texts
from db import database as db

logger = logging.getLogger(__name__)
router = Router()


# ─── Bat Swarm ────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith(bat_swarm.CALLBACK_PREFIX))
async def bat_swat_callback(call: CallbackQuery) -> None:
    if not call.data:
        return

    game_id_str = call.data.removeprefix(bat_swarm.CALLBACK_PREFIX)
    try:
        game_id = int(game_id_str)
    except ValueError:
        return

    round_data = bat_swarm.get_active_round(game_id)
    if not round_data:
        await call.answer("The bat already escaped. Too slow.", show_alert=False)
        return

    user_id = call.from_user.id
    player_ids: set[int] = round_data["player_ids"]

    if user_id not in player_ids:
        await call.answer("You're not in this game, Duke.", show_alert=False)
        return

    future = round_data["future"]
    if future.done():
        await call.answer("Someone was faster.", show_alert=False)
        return

    appeared_at: float = round_data["appeared_at"]
    reaction_ms = int((time.monotonic() - appeared_at) * 1000)

    future.set_result((user_id, reaction_ms))

    username = call.from_user.first_name or call.from_user.username or "Unknown"
    await call.answer(f"⚡ You hit it in {reaction_ms}ms!", show_alert=False)

    if call.message:
        await call.message.reply(
            texts.bat_winner(username, reaction_ms, max(30, 100 - reaction_ms // 10)),
            parse_mode="Markdown",
        )


# ─── Attorney's Advice ────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith(attorneys_advice.CALLBACK_PREFIX))
async def attorney_answer_callback(call: CallbackQuery) -> None:
    if not call.data:
        return

    payload = call.data.removeprefix(attorneys_advice.CALLBACK_PREFIX)
    try:
        game_id_str, choice_str = payload.rsplit(":", 1)
        game_id = int(game_id_str)
        chosen_idx = int(choice_str)
    except (ValueError, IndexError):
        return

    round_data = attorneys_advice.get_active_round(game_id)
    if not round_data:
        await call.answer("The question expired.", show_alert=False)
        return

    user_id = call.from_user.id
    player_ids: set[int] = round_data["player_ids"]
    answered: set[int] = round_data["answered"]

    if user_id not in player_ids:
        await call.answer("You're not in this game.", show_alert=False)
        return

    if user_id in answered:
        await call.answer("You already answered, Duke.", show_alert=False)
        return

    answered.add(user_id)
    correct_idx: int = round_data["correct_idx"]
    is_correct = chosen_idx == correct_idx

    username = call.from_user.first_name or call.from_user.username or "Unknown"

    future = round_data["future"]
    if is_correct and not future.done():
        future.set_result((user_id, True))
        await call.answer("✅ Correct!", show_alert=False)
    else:
        await call.answer("❌ Wrong.", show_alert=False)
        if call.message:
            await call.message.reply(
                texts.attorney_wrong(username),
                parse_mode="Markdown",
            )


# ─── Lizard Loyalty ───────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith(lizard_loyalty.CALLBACK_PREFIX))
async def lizard_answer_callback(call: CallbackQuery) -> None:
    if not call.data:
        return

    payload = call.data.removeprefix(lizard_loyalty.CALLBACK_PREFIX)
    try:
        game_id_str, choice_str = payload.rsplit(":", 1)
        game_id = int(game_id_str)
        chosen_idx = int(choice_str)
    except (ValueError, IndexError):
        return

    round_data = lizard_loyalty.get_active_round(game_id)
    if not round_data:
        await call.answer("The memory has faded.", show_alert=False)
        return

    user_id = call.from_user.id
    player_ids: set[int] = round_data["player_ids"]
    answered: set[int] = round_data["answered"]

    if user_id not in player_ids:
        await call.answer("You're not in this game.", show_alert=False)
        return

    if user_id in answered:
        await call.answer("You already answered.", show_alert=False)
        return

    answered.add(user_id)
    correct_idx: int = round_data["correct_idx"]
    is_correct = chosen_idx == correct_idx

    username = call.from_user.first_name or call.from_user.username or "Unknown"

    future = round_data["future"]
    if is_correct and not future.done():
        future.set_result((user_id, True))
        await call.answer("🦎 Correct! The lizards approve.", show_alert=False)
    else:
        await call.answer("❌ Wrong. The paranoia wins.", show_alert=False)
        if call.message:
            await call.message.reply(
                texts.lizard_wrong(username),
                parse_mode="Markdown",
            )
