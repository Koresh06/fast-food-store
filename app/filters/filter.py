from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class CheckImageFilter(BaseFilter): 
    
    async def __call__(self, message: Message) -> bool:  
        if message.photo:
            return True
        else:
            await message.answer('Это не изображение, отрпавьте еще раз!')
            return False
    
class IsDigitFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        try:
            if message.text.isdigit() and isinstance(float(message.text), float):
                return True
        except ValueError:
            await message.answer('Не корректно указан прайс, попробуйте еще раз!')
            return False
        