"""
Attorney's Advice — Logic / Attention Challenge.
Bot asks a Fear & Loathing flavored trivia question.
Multiple choice via inline buttons; first correct answer wins.
"""

import asyncio
import random

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from narrative import texts

POINTS_CORRECT_FIRST = 80
POINTS_CORRECT_LATER = 40
TIME_LIMIT = 20  # seconds
CALLBACK_PREFIX = "atty_ans:"

# ─── Question bank ────────────────────────────────────────────────────────────
# Each entry: (question, [choices], correct_index)
QUESTIONS = [
    (
        "We were somewhere around Barstow when the drugs began to take hold. "
        "What state were they driving through?",
        ["Nevada", "California", "Arizona", "New Mexico"],
        1,
    ),
    (
        "What is the name of Raoul Duke's attorney and companion?",
        ["Oscar Acosta", "Dr. Gonzo", "Chet Bly", "Dr. Pepper"],
        1,
    ),
    (
        "Which of these was NOT in the trunk according to Duke's inventory?",
        ["Mescaline", "High-powered blotter acid", "Tequila", "Amyl nitrite"],
        2,
    ),
    (
        "The American Dream, as understood by Raoul Duke, is best described as...",
        [
            "Freedom through hard work",
            "A cruel and shallow money trench",
            "The pursuit of happiness",
            "A hot dog stand in Vegas",
        ],
        1,
    ),
    (
        "What sport was Duke supposedly covering in Las Vegas?",
        ["Heavyweight boxing", "The Mint 400 off-road race", "Horse racing", "Poker tournament"],
        1,
    ),
    (
        "Fear and Loathing in Las Vegas was written by whom?",
        ["Tom Wolfe", "Ken Kesey", "Hunter S. Thompson", "Charles Bukowski"],
        2,
    ),
    (
        "What is Gonzo journalism?",
        [
            "Anonymous investigative reporting",
            "First-person immersive journalism with no separation from the story",
            "Satirical political cartoons",
            "Broadcast news from war zones",
        ],
        1,
    ),
    (
        "Duke's preferred substance for 'creative clarity' was which of these?",
        ["Bourbon", "Ether", "Caffeine pills", "Warm milk"],
        1,
    ),
    (
        "What does Duke famously say about the high-water mark?",
        [
            "We had crested it in Barstow",
            "There was a fantastic universal sense that whatever we were doing was right",
            "The wave broke and rolled back",
            "All of the above",
        ],
        3,
    ),
    (
        "Which Vegas hotel did Duke and his attorney primarily inhabit?",
        ["Caesars Palace", "The Sands", "Circus-Circus", "The Flamingo"],
        2,
    ),
    (
        "What animal hallucination greets Duke upon arriving in Vegas?",
        ["Snakes", "Giant bats", "Lizard people", "Scorpions"],
        1,
    ),
    (
        "The phrase 'Buy the ticket, take the ride' means...",
        [
            "Gamble responsibly",
            "If you choose the life, you live with the consequences",
            "Travel is educational",
            "Always use public transport",
        ],
        1,
    ),
]


def _make_keyboard(game_id: int, choices: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for i, choice in enumerate(choices):
        buttons.append([InlineKeyboardButton(
            text=f"{['A', 'B', 'C', 'D'][i]}. {choice}",
            callback_data=f"{CALLBACK_PREFIX}{game_id}:{i}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def run(
    bot: Bot,
    chat_id: int,
    game_id: int,
    player_ids: set[int],
) -> tuple[int | None, int]:
    """
    Returns (winning_user_id, points) or (None, 0).
    """
    question, choices, correct_idx = random.choice(QUESTIONS)

    await bot.send_message(
        chat_id,
        random.choice(texts.ATTORNEY_INTRO),
        parse_mode="Markdown",
    )

    q_msg = await bot.send_message(
        chat_id,
        texts.attorney_question_msg(question, TIME_LIMIT),
        reply_markup=_make_keyboard(game_id, choices),
        parse_mode="Markdown",
    )

    # Future resolves with (user_id, is_correct)
    result_future: asyncio.Future[tuple[int, bool]] = asyncio.get_event_loop().create_future()
    answered: set[int] = set()

    _active_rounds[game_id] = {
        "future": result_future,
        "correct_idx": correct_idx,
        "player_ids": player_ids,
        "answered": answered,
        "first_winner": None,
    }

    winner_id = None
    points = 0

    try:
        winner_id, correct = await asyncio.wait_for(result_future, timeout=TIME_LIMIT)
        if correct:
            points = POINTS_CORRECT_FIRST
        else:
            winner_id = None
    except asyncio.TimeoutError:
        winner_id = None

    _active_rounds.pop(game_id, None)

    # Disable keyboard
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=q_msg.message_id,
            reply_markup=None,
        )
    except Exception:
        pass

    correct_text = choices[correct_idx]

    if winner_id and points > 0:
        return winner_id, points
    else:
        await bot.send_message(
            chat_id,
            texts.ATTORNEY_TIMEOUT + "\n" + texts.ATTORNEY_CORRECT_REVEAL.format(answer=correct_text),
            parse_mode="Markdown",
        )
        return None, 0


# ─── Active round registry ────────────────────────────────────────────────────
_active_rounds: dict[int, dict] = {}


def get_active_round(game_id: int) -> dict | None:
    return _active_rounds.get(game_id)
