import os

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import requests

from AI import ChatGpt
from datetime import datetime

import app.keyboards as kb

load_dotenv()
router = Router()
users = dict()
errMessage = "Misuse detected. Please get in touch, we can come up with a solution for your use case."




class StateInfo(StatesGroup):
    city = State()


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await message.answer(f'Привет, {message.from_user.full_name}, Напиши название своего города, чтобы узнать погоду.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(StateInfo.city)


@router.message(F.text == "Сменить город")
async def select_city(message: Message, state: FSMContext):
    await state.set_state(StateInfo.city)
    await message.answer("Введите город", reply_markup=ReplyKeyboardRemove())


@router.message(StateInfo.city)
async def select_city_handler(message: Message, state: FSMContext):
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&units=metric&appid={os.getenv('OPEN_WEATHER_KEY')}')
    if (response.status_code == 200):
        data = response.json()
        await state.update_data(city = data["name"])
        user = dict()
        user.update({"city" : data["name"]})
        user.update({"weather" : " "})
        users.update({message.from_user.id : user})
        await state.clear()
        await message.answer(f"Отлично! теперь вы можете узнавать информацию о погоде в городе {data['name']}", reply_markup=kb.main)
    else:
        await message.answer("Некорректное название города, повторите ввод")
    


@router.message(F.text)
async def weather(message: Message):
    print(users)
    print(f'user - {message.from_user.full_name}')
    try:
        print(users[message.from_user.id]["city"])
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={users[message.from_user.id]["city"]}&lang=ru&units=metric&appid={os.getenv('OPEN_WEATHER_KEY')}')
        data = response.json()
        match message.text.lower():
            case "температура":
                 answer = f"Текущая темпераутра в городе {data["name"]} на {datetime.fromtimestamp(data['dt']).day}.{datetime.fromtimestamp(data['dt']).month}.{datetime.fromtimestamp(data['dt']).year} составляет {int(data['main']['temp'])}°C " \
                 f"(Ощущается как {int(data['main']['feels_like'])}°C)"
                 await message.answer(answer)
            case "вся информация о погоде":
                answer = f"Погода в городе {data["name"]} на {datetime.fromtimestamp(data['dt']).day}.{datetime.fromtimestamp(data['dt']).month}.{datetime.fromtimestamp(data['dt']).year}:\n" \
                f"{data['weather'][0]['description'].title()}\n"\
                f"Текущая темпераутра: {int(data['main']['temp'])}°C (Ощущается как {int(data['main']['feels_like'])}°C)\n" \
                f"Максимальная температура {int(data['main']['temp_max'])}°C, Минимальная температура {int(data['main']['temp_min'])}°C\n" \
                f"Ветер: {data['wind']['speed']} м/c\n" \
                f"Давление: {data['main']['pressure']} мм.рт.ст\n" \
                f"Влажность: {data['main']['humidity']}%\n"\
                f"Восход: {datetime.fromtimestamp(data["sys"]["sunrise"]).hour:02}:{datetime.fromtimestamp(data["sys"]["sunrise"]).minute:02}\n"\
                f"Закат: {datetime.fromtimestamp(data["sys"]["sunset"]).hour:02}:{datetime.fromtimestamp(data["sys"]["sunset"]).minute:02}"
                users[message.from_user.id]["weather"] = answer
                await message.answer(answer, reply_markup=kb.advice)  
            case "ветер":
                answer = f"Текущая скорость ветра в городе {data["name"]} на {datetime.fromtimestamp(data['dt']).day}.{datetime.fromtimestamp(data['dt']).month}.{datetime.fromtimestamp(data['dt']).year} составляет {data['wind']['speed']} м/c \n"
                await message.answer(answer)
            case "давление":
                answer = f"Текущее давление в городе {data["name"]} на {datetime.fromtimestamp(data['dt']).day}.{datetime.fromtimestamp(data['dt']).month}.{datetime.fromtimestamp(data['dt']).year} составляет {data['main']['pressure']} мм.рт.ст \n"
                await message.answer(answer)
            case "влажность":
                   answer = f"Текущая влажность в городе {data["name"]} на {datetime.fromtimestamp(data['dt']).day}.{datetime.fromtimestamp(data['dt']).month}.{datetime.fromtimestamp(data['dt']).year} составляет {data['main']['humidity']}% \n"
                   await message.answer(answer)
            case _:
                await message.answer("Некорректный запрос, нажмите кнопку на клавитуре")
                await message.answer_sticker("CAACAgIAAxkBAAELJghnanl409t_TNkHyFSmJVKYzvy_SQACGywAAq0KkUt8VblM6RlY6zYE")
        
    except:
        await message.answer_sticker("CAACAgIAAxkBAAELJghnanl409t_TNkHyFSmJVKYzvy_SQACGywAAq0KkUt8VblM6RlY6zYE")
        #await message.answer("Что то пошло не так, повторите ввод")


@router.callback_query(F.data == "advice")
async def get_advice(callback : CallbackQuery):
    await callback.answer('Загрузка совета...')
    await callback.message.edit_reply_markup()
    answer = ChatGpt.requestToAi(users[callback.from_user.id]["weather"])
    while (errMessage in answer):
        answer = ChatGpt.requestToAi(users[callback.from_user.id]["weather"])
    await callback.message.answer(answer)




