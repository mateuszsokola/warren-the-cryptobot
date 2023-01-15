import asyncio
from typing import Callable
from warren.utils.format_exception import format_exception
from warren.utils.logger import logger


class Runner:
    __shared_instance = None

    @staticmethod
    def getInstance():
        if Runner.__shared_instance is None:
            Runner()
        return Runner.__shared_instance

    def __init__(self):
        if Runner.__shared_instance is not None:
            raise Exception("This is a singleton, please use Runner.getInstance() to access it.")
        else:
            Runner.__shared_instance = self
            self.shutdown = False

    @staticmethod
    async def cancellable_sleep(time: int):
        task = asyncio.create_task(asyncio.sleep(time), name="cancellable_sleep")
        return await task

    @staticmethod
    def cancel_pending_tasks():
        for task in asyncio.all_tasks():
            if "cancellable_sleep" not in task.get_name():
                continue
            logger.info(f"{task.get_name()}: {task.get_coro().__name__} is shutting down...")
            try:
                task.cancel()
                logger.info(f"{task.get_name()}: {task.get_coro().__name__} cancelled successfully!")
            except Exception as ex:
                logger.info(f"{task.get_name()}: {task.get_coro().__name__} shutdown failed...")
                logger.info(f"{task.get_name()}: {ex}")

    async def with_loop(self, fn: Callable, interval: int, stop_on_exception=True):
        while True:
            try:
                await fn()
            except Exception as e:
                if stop_on_exception:
                    raise e
                else:
                    logger.error(format_exception())
            finally:
                if not self.shutdown:
                    await self.cancellable_sleep(interval)

    def graceful_shutdown(self, signal=None):
        if signal:
            logger.warning(f"Received exit signal {signal.name}...")

        logger.info("Warren shutting down...")
        self.shutdown = True
        self.cancel_pending_tasks()
