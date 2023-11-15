from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import config

# Это будет inner-мидлварь на сообщения
class Is_Admin(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Если сегодня не суббота и не воскресенье,
        # то продолжаем обработку.
        if event.from_user.id == config.ADMIN_ID:
            return await handler(event, data)
        await event.answer('Данная команда доступна только для администатора')
        return