"""
Peak Engine — orchestrates the full game cycle.
Runs N rounds of randomly selected challenges, awards points,
announces winners, and finalises scores.
"""

import asyncio
import random
import logging

from aiogram import Bot

from db import database as db
from narrative import texts
from challenges import bat_swarm, attorneys_advice, lizard_loyalty

logger = logging.getLogger(__name__)

ROUNDS = 5
BETWEEN_ROUND_DELAY = 3  # seconds

CHALLENGE_ROSTER = [
    bat_swarm,
    attorneys_advice,
    lizard_loyalty,
]


async def run_game(bot: Bot, chat_id: int, game_id: int) -> None:
    """Main game loop. Called from /begin handler."""
    await db.set_game_status(game_id, "running")

    players = await db.get_game_players(game_id)
    player_ids = {uid for uid, _ in players}
    player_names = {uid: name for uid, name in players}

    await bot.send_message(
        chat_id,
        texts.game_starting(len(players)),
        parse_mode="Markdown",
    )

    await asyncio.sleep(3)

    # ── rounds ────────────────────────────────────────────────────────────────
    # Shuffle so no challenge repeats consecutively if possible
    challenges = CHALLENGE_ROSTER.copy()
    round_deck: list = []

    for i in range(1, ROUNDS + 1):
        if not round_deck:
            round_deck = challenges * 2
            random.shuffle(round_deck)

        challenge = round_deck.pop()

        await bot.send_message(
            chat_id,
            texts.round_intro(i),
            parse_mode="Markdown",
        )
        await asyncio.sleep(2)

        try:
            winner_id, points = await challenge.run(
                bot=bot,
                chat_id=chat_id,
                game_id=game_id,
                player_ids=player_ids,
            )
        except Exception as exc:
            logger.exception("Challenge %s raised an error: %s", challenge.__name__, exc)
            winner_id, points = None, 0

        if winner_id and points > 0:
            winner_name = player_names.get(winner_id, "Unknown")
            await db.add_points(game_id, winner_id, points)

            # pick appropriate winner message
            if challenge is bat_swarm:
                # reaction_ms is baked into the challenge; we use a simplified msg
                msg = texts.bat_winner(winner_name, 0, points).replace(" in *0ms*", "")
            elif challenge is attorneys_advice:
                msg = texts.attorney_winner(winner_name, points)
            else:
                msg = texts.lizard_winner(winner_name, points)

            await bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            await bot.send_message(
                chat_id, texts.NO_WINNER_THIS_ROUND, parse_mode="Markdown"
            )

        # Show mid-game scores every 2 rounds
        if i % 2 == 0 and i < ROUNDS:
            scores = await db.get_game_scores(game_id)
            await bot.send_message(
                chat_id,
                texts.scoreboard(scores, title=f"STANDINGS AFTER ROUND {i}"),
                parse_mode="Markdown",
            )

        if i < ROUNDS:
            await bot.send_message(
                chat_id, texts.between_rounds(), parse_mode="Markdown"
            )
            await asyncio.sleep(BETWEEN_ROUND_DELAY)

    # ── game over ─────────────────────────────────────────────────────────────
    await db.set_game_status(game_id, "finished")
    await db.finalize_scores(game_id)

    final_scores = await db.get_game_scores(game_id)

    if not final_scores:
        await bot.send_message(chat_id, "The journey ends with no survivors.", parse_mode="Markdown")
        return

    top_score = final_scores[0][1]
    winners = [name for name, pts in final_scores if pts == top_score]

    if len(winners) > 1:
        board = texts.scoreboard(final_scores, title="FINAL STANDINGS")
        msg = texts.GAME_OVER_TIE.format(board=board)
    else:
        msg = texts.game_over(winners[0], final_scores)

    await bot.send_message(chat_id, msg, parse_mode="Markdown")
