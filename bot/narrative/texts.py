"""
All gonzo flavor text for The Savage Journey.
Fear and Loathing in Las Vegas — the party game.
"""

import random

# ─── Bot intro ────────────────────────────────────────────────────────────────

INTRO = (
    "🦇 *THE SAVAGE JOURNEY*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "We were somewhere around Barstow, on the edge of the desert, when the drugs "
    "began to take hold. And suddenly there was a terrible roar all around us and "
    "the sky was full of what looked like huge bats, all swooping and screeching "
    "and diving around the car...\n\n"
    "Welcome to _The Savage Journey_ — a group party game for those who have "
    "committed themselves fully to the American Dream.\n\n"
    "⚠️ *This message will self-destruct when the ether wears off.*"
)

HELP_TEXT = (
    "🦇 *THE SAVAGE JOURNEY — FIELD MANUAL*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "*/join* — Enlist in the journey. Must be done in a group.\n"
    "*/begin* — Unleash the peak cycle. Requires 2+ players.\n"
    "*/score* — Check who's winning the American Dream.\n"
    "*/end* — Abort the mission (admin only).\n"
    "*/help* — You're reading it, Duke.\n\n"
    "_The challenges:_\n"
    "🦇 *Bat Swarm* — Reaction speed. First to slap the bat wins.\n"
    "⚖️ *Attorney's Advice* — Logic under pressure. Answer correctly.\n"
    "🦎 *Lizard Loyalty* — Memory and paranoia. Remember the sequence.\n\n"
    "Good luck. You're going to need it."
)

# ─── Game state messages ──────────────────────────────────────────────────────

LOBBY_OPEN = (
    "🦇 *A NEW SAVAGE JOURNEY BEGINS*\n\n"
    "The trunk is packed. The ether is open. The bats are circling.\n\n"
    "Use /join to enlist in this expedition. You'll need at least 2 "
    "deranged individuals before the peak cycle can begin.\n\n"
    "When the crew is assembled, use /begin to cross the line into total madness."
)

def player_joined(username: str, count: int) -> str:
    lines = [
        f"✅ *{username}* has climbed into the convertible. ({count} aboard)",
        f"✅ *{username}* has joined the expedition. ({count} in the trunk)",
        f"✅ *{username}* stumbled in from the desert. ({count} survivors so far)",
        f"✅ *{username}* checked in. The doctor says {count} are stable.",
    ]
    return random.choice(lines)

def already_joined(username: str) -> str:
    return f"⚠️ *{username}*, you're already in the car. Stop falling out."

NOT_IN_GROUP = (
    "🦇 This command only works in a group chat, Duke. "
    "Find some companions and add me to a group."
)

NO_GAME_RUNNING = (
    "⚠️ No journey is currently in progress. "
    "Someone needs to start one — the desert won't wait forever."
)

NOT_ENOUGH_PLAYERS = (
    "⚠️ *Not enough players.*\n\n"
    "You need at least 2 willing participants before we can begin. "
    "The American Dream requires witnesses."
)

GAME_ALREADY_RUNNING = (
    "⚠️ A journey is already underway. "
    "Let the madness play out before starting a new one."
)

def game_starting(player_count: int) -> str:
    return (
        f"🦇 *THE PEAK CYCLE BEGINS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{player_count} souls have committed to the journey.\n\n"
        f"We had two bags of grass, seventy-five pellets of mescaline, "
        f"five sheets of high-powered blotter acid, a salt shaker half full "
        f"of cocaine, and a whole galaxy of multi-colored uppers, downers, "
        f"screamers, laughers... and also five rounds of challenges.\n\n"
        f"_Strap in. It's going to get weird._"
    )

# ─── Round transitions ────────────────────────────────────────────────────────

ROUND_INTROS = [
    "🎲 *ROUND {n}* — The walls are breathing...",
    "🎲 *ROUND {n}* — Stay sharp. Or don't. It won't matter either way.",
    "🎲 *ROUND {n}* — The bats are getting closer.",
    "🎲 *ROUND {n}* — Your attorney advises you to continue.",
    "🎲 *ROUND {n}* — Something in the ether says push forward.",
]

def round_intro(n: int) -> str:
    return random.choice(ROUND_INTROS).format(n=n)

# ─── Bat Swarm challenge ──────────────────────────────────────────────────────

BAT_SWARM_INTRO = [
    "🦇 *BAT SWARM*\n\nThey came without warning — a shrieking cloud of "
    "leather wings and teeth. *First one to SWAT THE BAT wins the round!*",

    "🦇 *BAT SWARM*\n\nSomething in the sky has gone wrong. Very wrong. "
    "The bats are here and they want something from you. "
    "*Hit that button before anyone else does!*",

    "🦇 *BAT SWARM*\n\nWe had driven maybe 100 miles when the bats appeared. "
    "No time to think. *Reaction speed is all that matters now.*",
]

BAT_SWARM_WAITING = [
    "👀 _Watch the skies... they're coming..._",
    "👀 _Stay focused. The bats don't give warnings._",
    "👀 _Don't blink. Don't even breathe._",
]

BAT_BUTTON = "🦇 SWAT THE BAT!"

def bat_winner(username: str, reaction_ms: int, points: int) -> str:
    return (
        f"⚡ *{username}* slapped the bat in *{reaction_ms}ms!*\n"
        f"_{points} points added to their account with the Universe._"
    )

BAT_TOO_SLOW = "💨 _The bat escaped. Nobody was fast enough. The points vanish into the desert._"

BAT_FALSE_START = "🚫 *FALSE START!* The bat wasn't there yet. Patience, Duke."

# ─── Attorney's Advice challenge ─────────────────────────────────────────────

ATTORNEY_INTRO = [
    "⚖️ *ATTORNEY'S ADVICE*\n\nMy attorney leaned over and whispered "
    "something I'll never forget. Now you have to figure out what it was. "
    "*Read carefully. One correct answer. Don't blow it.*",

    "⚖️ *ATTORNEY'S ADVICE*\n\nThe law is a blunt instrument. "
    "So is stupidity. This round tests which one you have more of. "
    "*Choose wisely.*",

    "⚖️ *ATTORNEY'S ADVICE*\n\nIn this business you need a good attorney "
    "and an even better memory. *Answer the question correctly for full points.*",
]

def attorney_question_msg(question: str, time_limit: int) -> str:
    return (
        f"⚖️ *{question}*\n\n"
        f"_You have {time_limit} seconds. Your attorney is watching._"
    )

def attorney_winner(username: str, points: int) -> str:
    phrases = [
        f"✅ *{username}* got it right! The attorney nods approvingly. *+{points} pts*",
        f"✅ *{username}* — correct! Buy that man/woman a drink. *+{points} pts*",
        f"✅ *{username}* answered correctly. The law smiles upon them. *+{points} pts*",
    ]
    return random.choice(phrases)

def attorney_wrong(username: str) -> str:
    phrases = [
        f"❌ *{username}* — wrong. Your attorney is horrified.",
        f"❌ *{username}* — incorrect. Even the lizards knew that one.",
        f"❌ *{username}* — not quite. Back to the trunk with you.",
    ]
    return random.choice(phrases)

ATTORNEY_TIMEOUT = (
    "⏰ *Time's up.* Nobody answered correctly. "
    "The attorney bills you anyway."
)

ATTORNEY_CORRECT_REVEAL = "✅ The correct answer was: *{answer}*"

# ─── Lizard Loyalty challenge ─────────────────────────────────────────────────

LIZARD_INTRO = [
    "🦎 *LIZARD LOYALTY*\n\nThe desert teaches you one thing: "
    "trust no one, remember everything. "
    "*Study the sequence. It will not be shown again.*",

    "🦎 *LIZARD LOYALTY*\n\nThe lizards know the order of things. "
    "Do you? *Memorize the sequence before it disappears.*",

    "🦎 *LIZARD LOYALTY*\n\nParanoia is a survival skill. "
    "So is memory. *Learn the pattern. Prove your loyalty.*",
]

def lizard_sequence_display(items: list) -> str:
    return (
        "🦎 *REMEMBER THIS SEQUENCE:*\n\n"
        + "  →  ".join(items)
        + "\n\n_Burning it into your skull... disappears in 5 seconds..._"
    )

def lizard_question(question: str, time_limit: int) -> str:
    return (
        f"🦎 *{question}*\n\n"
        f"_You have {time_limit} seconds. The sequence is gone now._"
    )

def lizard_winner(username: str, points: int) -> str:
    phrases = [
        f"🦎 *{username}* remembered! The lizards approve. *+{points} pts*",
        f"🦎 *{username}* — correct! Memory like a steel trap. *+{points} pts*",
        f"🦎 *{username}* — right answer! The desert nods. *+{points} pts*",
    ]
    return random.choice(phrases)

def lizard_wrong(username: str) -> str:
    phrases = [
        f"❌ *{username}* — the lizards are disappointed.",
        f"❌ *{username}* — wrong sequence. The paranoia wins.",
        f"❌ *{username}* — incorrect. Were you even paying attention?",
    ]
    return random.choice(phrases)

LIZARD_TIMEOUT = (
    "⏰ *Nobody remembered.* The sequence is lost to the desert. "
    "No points for anyone."
)

# ─── Scoreboard ──────────────────────────────────────────────────────────────

def scoreboard(scores: list[tuple[str, int]], title: str = "CURRENT STANDINGS") -> str:
    if not scores:
        return "📊 *No scores yet.* The journey has just begun."

    medals = ["🥇", "🥈", "🥉"]
    lines = [f"📊 *{title}*", "━━━━━━━━━━━━━━━━━━━━━━"]
    for i, (name, pts) in enumerate(scores):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{medal} *{name}* — {pts} pts")
    return "\n".join(lines)

# ─── Game over ────────────────────────────────────────────────────────────────

def game_over(winner: str, scores: list[tuple[str, int]]) -> str:
    board = scoreboard(scores, title="FINAL STANDINGS")
    return (
        f"🏁 *THE SAVAGE JOURNEY ENDS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏆 *{winner}* has claimed the American Dream!\n\n"
        f"{board}\n\n"
        f"_We are all wired into a survival trip now. No more of the "
        f"speed that fueled the first 50 miles. This is the ether hour._\n\n"
        f"Start a new game with /begin when the dust settles."
    )

GAME_OVER_TIE = (
    "🏁 *THE SAVAGE JOURNEY ENDS*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🤝 *It's a TIE.* The American Dream belongs to everyone equally.\n\n"
    "{board}\n\n"
    "_Nobody wins. Nobody loses. The desert takes it all._"
)

GAME_ABORTED = (
    "⛔ *THE JOURNEY HAS BEEN ABORTED.*\n\n"
    "The mission is scrubbed. The bats return to their caves. "
    "Start again when you're ready with /begin."
)

# ─── Generic flavor ──────────────────────────────────────────────────────────

BETWEEN_ROUNDS = [
    "_The ether is wearing thin... brace yourself..._",
    "_Your attorney refills his glass. Next round incoming._",
    "_The bats regroup in the rafters..._",
    "_Something is shifting in the fabric of the game..._",
]

def between_rounds() -> str:
    return random.choice(BETWEEN_ROUNDS)

NO_WINNER_THIS_ROUND = (
    "💨 _Nobody scored this round. The desert claims what's owed._"
)
