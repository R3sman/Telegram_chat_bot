from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
import asyncio
from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


bot = Bot(
    token='Ваш токен',
    default=DefaultBotProperties(parse_mode="HTML", protect_content=False),
)
dp = Dispatcher()

class HelpAvto(StatesGroup):
    choosing_avto = State()
    select_problem = State()

@dp.message(CommandStart, StateFilter(None))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f"Введите модель автомобиля")
    await state.set_state(HelpAvto.choosing_avto)

@dp.message(HelpAvto.choosing_avto)
async def cmd_start(message: types.Message, state: FSMContext):
    avto_model = message.text
    # Здесь ваша проверка на наличие автомобиля в списке
    # Предположим что у вас есть функция на проверку автомобиля check_avto(),
    # которая возвращает True или False
    # хотя лучше это реализовать без доп. функций
    def check_avto(avto_model):
        return avto_model != None
    if check_avto(avto_model):
        await message.answer('Введите вашу проблему')
        await state.set_state(HelpAvto.select_problem)
    else:
        await message.answer('Мы не знаем такую машину(')
        await state.set_state(None)
    await state.set_state(HelpAvto.choosing_avto)

@dp.message(HelpAvto.select_problem)
async def cmd_start(message: types.Message, state: FSMContext):
    problem = message.text
    # здесь функция возвращающая текст ответа llm
    # допустим пусть она называется resolve_problem
    def resolve_problem(problem):
        return 'some answer'
    await message.answer(f'{resolve_problem(problem)}')
    await state.set_state(None)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())