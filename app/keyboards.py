from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Температура'), KeyboardButton(text='Ветер'), KeyboardButton(text='Давление'), KeyboardButton(text='Влажность')],
    [KeyboardButton(text='Вся информация о погоде')],
    [KeyboardButton(text='Сменить город')]
], 
resize_keyboard= True, input_field_placeholder="Нажите кнопку")

advice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Совет', callback_data='advice')]
])


