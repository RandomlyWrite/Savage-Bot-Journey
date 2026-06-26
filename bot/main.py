"""
The Savage Journey — entry point.
Fear and Loathing in Las Vegas group party game bot.
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from db.database import init_db
from handlers.commands import router as commands_router
from handlers.callbacks import router as callbacks_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Add it as a Secret in Replit before starting the bot."
        )

    logger.info("Initialising database...")
    await init_db()

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher()

    # Register routers — callbacks first (more specific)
    dp.include_router(callbacks_router)
    dp.include_router(commands_router)

    logger.info("The Savage Journey bot is starting. We were somewhere around Barstow...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
