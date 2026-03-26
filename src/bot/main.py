import asyncio
import signal

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError, TelegramUnauthorizedError
from structlog import get_logger

from src.bot.handlers.admin import router as admin_router
from src.bot.handlers.callbacks import router as callbacks_router
from src.bot.handlers.commands import router as commands_router
from src.config.logging import configure_logging
from src.config.settings import get_settings

logger = get_logger(__name__)


async def _wait_until_telegram_api_reachable(bot: Bot) -> None:
    """Повторяет get_me(), пока не удастся достучаться до api.telegram.org (VPN/фаервол/прокси)."""
    delay = 5.0
    max_delay = 60.0
    attempt = 0
    while True:
        try:
            me = await bot.get_me()
            logger.info("telegram_api_connected", bot_username=me.username, bot_id=me.id)
            return
        except TelegramUnauthorizedError:
            logger.error("telegram_invalid_token")
            raise
        except TelegramAPIError as exc:
            attempt += 1
            logger.warning(
                "telegram_api_unreachable",
                attempt=attempt,
                error=str(exc),
                hint=(
                    "Нет исходящего HTTPS к api.telegram.org:443 из контейнера. "
                    "Проверьте фаервол, VPN на хосте, DNS; при необходимости задайте HTTP_PROXY/HTTPS_PROXY."
                ),
            )
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, max_delay)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(commands_router)
    dispatcher.include_router(admin_router)
    dispatcher.include_router(callbacks_router)

    stop_event = asyncio.Event()

    def _stop_handler() -> None:
        logger.info("bot_shutdown_signal_received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop_handler)
        except NotImplementedError:
            pass

    await _wait_until_telegram_api_reachable(bot)

    polling_task = asyncio.create_task(dispatcher.start_polling(bot))
    stop_task = asyncio.create_task(stop_event.wait())
    done, pending = await asyncio.wait(
        {polling_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()
    if stop_task in done and not polling_task.done():
        polling_task.cancel()
    await bot.session.close()
    logger.info("bot_stopped")


if __name__ == "__main__":
    asyncio.run(main())
