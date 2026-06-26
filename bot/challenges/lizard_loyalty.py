"""
Lizard Loyalty — Paranoia / Memory Challenge.
Bot shows a sequence of emoji/items for a few seconds, then asks a question about it.
First correct answer wins.
"""

import asyncio
import random

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from narrative import texts

DISPLAY_SECONDS = 5
TIME_LIMIT = 15
POINTS_WIN = 90
CALLBACK_PREFIX = "liz_ans:"

# ─── Sequence pools ───────────────────────────────────────────────────────────

ITEM_POOLS = [
    ["🦇", "🦎", "🌵", "🎰", "🍺", "🔫", "💊", "🎲"],
    ["🌮", "🎸", "🏜️", "🚗", "👓", "🎩", "🐍", "🌙"],
    ["⚡", "🍋", "🔑", "🎯", "🃏", "🦅", "🌊", "🔮"],
]

SEQUENCE_LENGTH = 4  # items shown


def _build_sequence() -> list[str]:
    pool = random.choice(ITEM_POOLS)
    return random.sample(pool, SEQUENCE_LENGTH)


def _make_question_and_answers(seq: list[str]) -> tuple[str, list[str], int]:
    """Returns (question_text, [choices], correct_choice_index)."""
    question_type = random.choice(["position", "count", "missing"])

    if question_type == "position":
        pos = random.randint(0, SEQUENCE_LENGTH - 1)
        correct = seq[pos]
        ordinals = ["first", "second", "third", "fourth"]
        question = f"What was the *{ordinals[pos]}* item in the sequence?"
        # Build wrong answers from other pool items
        pool = [item for item in ITEM_POOLS[0] + ITEM_POOLS[1] + ITEM_POOLS[2]
                if item not in seq]
        wrongs = random.sample(pool, 3)
        choices = wrongs + [correct]
        random.shuffle(choices)
        correct_idx = choices.index(correct)

    elif question_type == "count":
        # Ask how many items were in the sequence
        correct = str(SEQUENCE_LENGTH)
        wrongs = [str(SEQUENCE_LENGTH - 1), str(SEQUENCE_LENGTH + 1), str(SEQUENCE_LENGTH + 2)]
        question = "How many items were in the sequence?"
        choices = wrongs + [correct]
        random.shuffle(choices)
        correct_idx = choices.index(correct)

    else:  # missing
        # Show 3 of the 4 items, ask what's missing
        shown_seq = seq[:-1]  # hide last item
        missing = seq[-1]
        pool = [item for item in ITEM_POOLS[0] + ITEM_POOLS[1] + ITEM_POOLS[2]
                if item not in seq]
        wrongs = random.sample(pool, 3)
        choices = wrongs + [missing]
        random.shuffle(choices)
        correct_idx = choices.index(missing)
        question = f"Which item was *missing* from this partial sequence: {' → '.join(shown_seq)} → ?"

    return question, choices, correct_idx


def _make_keyboard(game_id: int, choices: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for i, choice in enumerate(choices):
        buttons.append([InlineKeyboardButton(
            text=choice,
            callback_data=f"{CALLBACK_PREFIX}{game_id}:{i}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def run(
    bot: Bot,
    chat_id: int,
    game_id: int,
    player_ids: set[int],
) -> tuple[int | None, int]:
    """Returns (winning_user_id, points) or (None, 0)."""
    seq = _build_sequence()

    await bot.send_message(
        chat_id,
        random.choice(texts.LIZARD_INTRO),
        parse_mode="Markdown",
    )

    # Show sequence
    seq_msg = await bot.send_message(
        chat_id,
        texts.lizard_sequence_display(seq),
        parse_mode="Markdown",
    )

    await asyncio.sleep(DISPLAY_SECONDS)

    # Delete the sequence message
    try:
        await bot.delete_message(chat_id, seq_msg.message_id)
    except Exception:
        pass

    # Build question
    question, choices, correct_idx = _make_question_and_answers(seq)

    q_msg = await bot.send_message(
        chat_id,
        texts.lizard_question(question, TIME_LIMIT),
        reply_markup=_make_keyboard(game_id, choices),
        parse_mode="Markdown",
    )

    result_future: asyncio.Future[tuple[int, bool]] = asyncio.get_event_loop().create_future()

    _active_rounds[game_id] = {
        "future": result_future,
        "correct_idx": correct_idx,
        "player_ids": player_ids,
        "answered": set(),
    }

    winner_id = None
    points = 0

    try:
        winner_id, correct = await asyncio.wait_for(result_future, timeout=TIME_LIMIT)
        if correct:
            points = POINTS_WIN
        else:
            winner_id = None
    except asyncio.TimeoutError:
        winner_id = None

    _active_rounds.pop(game_id, None)

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=q_msg.message_id,
            reply_markup=None,
        )
    except Exception:
        pass

    if winner_id and points > 0:
        return winner_id, points
    else:
        await bot.send_message(chat_id, texts.LIZARD_TIMEOUT, parse_mode="Markdown")
        return None, 0


# ─── Active round registry ────────────────────────────────────────────────────
_active_rounds: dict[int, dict] = {}


def get_active_round(game_id: int) -> dict | None:
    return _active_rounds.get(game_id)
