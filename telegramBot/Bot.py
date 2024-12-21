import asyncio
import json
import requests
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext  # Исправленный импорт
from aiogram.fsm.state import State, StatesGroup  # Исправленный импорт

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
bot = Bot(token='')
dp = Dispatcher()

# ID администратора
MyID = ''

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Прайс лист")],
        [KeyboardButton(text="Запись на услугу")]
    ],
    resize_keyboard=True
)

# Кнопки для выбора услуг в прайс листе (с эмодзи)
price_list_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Психотравмы, доставшиеся от родителей 🤔")],
        [KeyboardButton(text="Ядро личности 😎")],
        [KeyboardButton(text="Сфера финансов 💸")],
        [KeyboardButton(text="Сфера любви ❤️")]
    ],
    resize_keyboard=True
)

# Кнопки для выбора услуг при записи на услугу (без эмодзи)
booking_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Психотравмы, доставшиеся от родителей")],
        [KeyboardButton(text="Ядро личности")],
        [KeyboardButton(text="Сфера финансов")],
        [KeyboardButton(text="Сфера любви")]
    ],
    resize_keyboard=True
)

# Кнопка для возвращения в главное меню
back_button = KeyboardButton(text="Назад")
back_menu = ReplyKeyboardMarkup(
    keyboard=[[back_button]],
    resize_keyboard=True
)

# Описание услуг
services_info = {
    "Сфера любви": (
        "Любовь очень сложная тема, но мы ответим на главные вопросы, которые помогут Вам разобраться в ней. А именно мы рассмотрим:\n"
        "• Истинный запрос\n"
        "• Какая жена\n"
        "• Какая любовница\n"
        "• Какой будущий муж\n"
        "• Какой любовник\n"
        "• Анализ 5 и 7 дома"
    ),
    "Сфера финансов": (
        "Любой человек мечтает о том, чтобы в будущем работать только на своем месте, в котором ему будет комфортно. Но где же этот комфорт? Для нахождения своей 'золотой жилы', я отвечу Вам на следующие вопросы:\n"
        "• Блоки/установки/страхи\n"
        "• В какой сфере развиваться\n"
        "• Найм/фриланс/бизнес\n"
        "• Тратить или копить\n"
        "• Как распоряжаться деньгами\n"
        "• Ваша ниша"
    ),
    "Ядро личности": (
        "Иногда мы сами не понимаем, кто мы. Я могу помочь разобраться, раскрывая следующие темы:\n"
        "• Внутреннее Я\n"
        "• Внешнее Я\n"
        "• Асцендент"
    ),
    "Психотравмы, доставшиеся от родителей": (
        "Что именно досталось нам от родителей? В чем мой талант?\n"
        "• Психологические родители\n"
        "• Психотравмы\n"
        "• Таланты\n"
        "• Реальные родители"
    )
}

# Цены для каждой услуги
prices = {
    "Психотравмы, доставшиеся от родителей 🤔": "300 р.",
    "Ядро личности 😎": "300 р.",
    "Сфера финансов 💸": "500 р.",
    "Сфера любви ❤️": "500 р."
}

# Регулярное выражение для проверки корректности данных
birth_info_pattern = r"^(\d{2}:\d{2})\s+(\d{2}\.\d{2}\.\d{4})\s+([A-Za-zА-Яа-яЁё\s]+)$"

# Кнопки для выбора формата
response_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ответ")],
        [KeyboardButton(text="Конференция (доплата 500 р.)")]
    ],
    resize_keyboard=True
)

# Создаём состояние для процесса записи на услугу
class Form(StatesGroup):
    waiting_for_service = State()  # Ждём выбора услуги
    waiting_for_details = State()  # Ждём данные для конференции


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = (
        "Привет! Недавно я прошла обучение по астрологии и тем самым осуществила свою заветную мечту!🌟\n"
        "Я не просто изучала планеты и их аспекты, но также их влияние на человека. Мы изучали себя в плоть до психотравм и не только!\n"
        "Да-да, ведь влияние планет при рождении человека настолько велико, что определяет его характер и судьбу!\n"
        "Я изучала такие темы как:\n"
        "1) Психотравмы, доставшиеся от родителей 🤔\n"
        "2) Ядро личности 😎\n"
        "3) Сфера финансов 💸\n"
        "4) Сфера любви ❤️"
    )
    await message.reply(welcome_text, reply_markup=main_menu)


# Обработчик "Прайс лист"
@dp.message(F.text == "Прайс лист")
async def price_list(message: types.Message):
    await message.reply("Выберите услугу для просмотра цены:", reply_markup=price_list_menu)


# Обработчик выбора услуги из прайс-листа
@dp.message(F.text.in_(prices.keys()))
async def show_price(message: types.Message):
    service_name = message.text
    price = prices.get(service_name)
    await message.reply(f"Цена услуги: {price}", reply_markup=main_menu)


# Обработчик "Запись на услугу"
@dp.message(F.text == "Запись на услугу")
async def service_booking(message: types.Message):
    await message.reply("Выберите услугу:", reply_markup=booking_menu)
    # Переходим в состояние ожидания услуги
    await Form.waiting_for_service.set()


# Обработчик выбора услуги при записи на услугу
@dp.message(F.text.in_(services_info.keys()))
async def show_service_details(message: types.Message, state: FSMContext):
    service_name = message.text
    info = services_info.get(service_name)
    await message.reply(info, reply_markup=response_menu)

    # Переходим в состояние ожидания выбора формата
    await Form.waiting_for_details.set()


# Обработчик "Ответ" или "Конференция"
@dp.message(F.text.in_(["Ответ", "Конференция (доплата 500 р.)"]))
async def select_format(message: types.Message, state: FSMContext):
    if message.text == "Ответ":
        await message.reply("Вы выбрали формат *Ответ*. Спасибо за выбор! Мы приступаем к работе.", reply_markup=main_menu)
    elif message.text == "Конференция (доплата 500 р.)":
        await message.reply("Вы выбрали формат *Конференция*. Пожалуйста, введите время, дату и место, чтобы я могла отправить их администратору.", reply_markup=back_menu)


# Обработчик данных для конференции
@dp.message(lambda message: re.match(birth_info_pattern, message.text.strip()))
async def handle_conference_data(message: types.Message):
    match = re.match(birth_info_pattern, message.text.strip())
    time, date, place = match.groups()

    # Получаем тэг пользователя
    user_tag = f"@{message.from_user.username}" if message.from_user.username else f"Пользователь {message.from_user.id}"

    print(time)
    # КАРОЧЕ ТУТ НАЧИНАЕТСЯ ОТПРАВКА ЗАПРОСА НА ПРОВЕРКУ ВРЕМЕНИ

    data = {

        'date': f'{date[6:]}-{date[3:5]}-{date[:2]}T{time}:00Z'
	}
    resp = {
        'exists': '',
    }
    json_data = json.dumps(data)
    print(json_data)

    header = {
        'Content-Type': 'application/json'
    }
    response = requests.get('http://localhost:8082/checkDate', headers=header, data=json_data)
    exist = response.json().get("exists")
    print(exist)

    if exist == True:
        # await bot.send_message(
        # chat_id=MyID,
        # text=f"📩 Извините, время занято!:\n\n"
        # f"{time,}"
        # )
        await message.reply("📩 Извините, время занято!:\n\n", reply_markup=main_menu)
    else:
         # Отправляем администратору данные для конференции, включая тэг пользователя ЕСЛИ ВРЕМЯ СВОБОДНО
        await bot.send_message(
        chat_id=MyID,
        text=f"📩 Новый запрос на конференцию:\n\n"
             f"Время: {time}\nДата: {date}\nМесто: {place}\n"
             f"Тэг пользователя: {user_tag}"
             f"{resp}"

        )

        data = {
            'year': int(date[6:]),
            'month': int(date[3:5]),
            'day': int(date[:2]),
            'hours': int(time[:2]),
            'minutes': int(time[3:]),
            'seconds': 0,
            'firstName': "isha",
            'midName': "anov",
            'lastName': "anovic",
            'service': "tarro",
            'online': True
            }
        # resp = {
        #     'exists': '',
        # }
        json_data = json.dumps(data)
        # print(json_data)

        header = {
            'Content-Type': 'application/json'
        }
        response = requests.post('http://localhost:8082/newAppointment', headers=header, data=json_data)
        # exist = response.json().get("exists")
        # Подтверждение пользователю
        await message.reply("Ваши данные были отправлены администратору! Мы свяжемся с вами для дальнейших шагов.", reply_markup=main_menu)





# Завершаем процесс в случае, если пользователь готов
@dp.message(F.text == "Назад")
async def go_back(message: types.Message):
    # Возвращаем в главное меню
    await message.reply("Вы в главном меню.", reply_markup=main_menu)


async def main():
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
