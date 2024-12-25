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
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
bot = Bot(token='token')
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
        [KeyboardButton(text="Психотравмы от родителей 🤔")],
        [KeyboardButton(text="Ядро личности 😎")],
        [KeyboardButton(text="Сфера финансов 💸")],
        [KeyboardButton(text="Сфера любви ❤️")]
    ],
    resize_keyboard=True
)

# Кнопки для выбора услуг при записи на услугу (без эмодзи)
booking_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Психотравмы от родителей")],
        [KeyboardButton(text="Ядро личности")],
        [KeyboardButton(text="Сфера финансов")],
        [KeyboardButton(text="Сфера любви")]
    ],
    resize_keyboard=True
)

# Кнопка "Меню" для завершения записи
menu_button = KeyboardButton(text="Меню")
menu_menu = ReplyKeyboardMarkup(
    keyboard=[[menu_button]],
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
    "Психотравмы от родителей": (
        "Что именно досталось нам от родителей? В чем мой талант?\n"
        "• Психологические родители\n"
        "• Психотравмы\n"
        "• Таланты\n"
        "• Реальные родители"
    )
}

# Цены для каждой услуги
prices = {
    "Психотравмы от родителей 🤔": "300 р.",
    "Ядро личности 😎": "300 р.",
    "Сфера финансов 💸": "500 р.",
    "Сфера любви ❤️": "500 р."
}

# Регулярные выражения для даты и времени
date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"  # Дата: ДД.ММ.ГГГГ
time_pattern = r"^(?P<time>\d{2}:\d{2})\s+(?P<lastname>[А-Яа-яЁё]+)\s+(?P<firstname>[А-Яа-яЁё]+)\s+(?P<midname>[А-Яа-яЁё]+)$"  # Время: ЧЧ:ММ
menu_pattern = r"^Меню$"  # Проверка для кнопки "Меню"

# Массив с доступными временными слотами
available_times = ["12:00", "13:00", "16:00", "17:00"]

# Кнопки для выбора формата
response_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ответ")],
        [KeyboardButton(text="Конференция (доплата 500 р.)")]
    ],
    resize_keyboard=True
)

# Создаем состояние для процесса записи на услугу
class Form(StatesGroup):
    waiting_for_service = State()  # Ждём выбора услуги
    waiting_for_details = State()  # Ждём данные для конференции
    waiting_for_date = State()  # Ждём дату для конференции
    waiting_for_time = State()  # Ждём время для конференции



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
    await state.update_data(service_name=service_name)
    await message.reply(info, reply_markup=response_menu)

    # Переходим в состояние ожидания выбора формата
    await state.set_data(Form.waiting_for_details)


# Обработчик "Ответ" или "Конференция"
@dp.message(F.text.in_(["Ответ", "Конференция (доплата 500 р.)"]))
async def select_format(message: types.Message, state: FSMContext):
    if message.text == "Ответ":
        await message.reply("Вы выбрали формат *Ответ*. Спасибо за выбор! Мы приступаем к работе.", reply_markup=main_menu)

        # # # Опционально

        # user_data = await state.get_data()
        # data = {
        #     'date': '0001-01-01T00:00:00Z',
        #     'firstName': str(message.from_user.full_name),
        #     'midName': str(message.from_user.username),
        #     'lastName': str(message.from_user.id),
        #     'service': user_data.get("service_name"),
        #     'online': False
        #     }
        # json_data = json.dumps(data)
        # header = {
        #     'Content-Type': 'application/json'
        # }
        # requests.post('http://localhost:8082/newAppointment', headers=header, data=json_data)

    elif message.text == "Конференция (доплата 500 р.)":
        # Отправляем сообщение с просьбой ввести дату
        await message.reply("Вы выбрали формат *Конференция*. Пожалуйста, введите дату, когда вы хотите провести конференцию (формат - ДД.ММ.ГГГГ).", reply_markup=menu_menu)
        # Переходим в состояние ожидания даты
        await state.set_state(Form.waiting_for_date)


# Обработчик получения даты (можно ввести как дату ДД.ММ.ГГГГ, так и время ЧЧ:ММ)
@dp.message(F.text, Form.waiting_for_date)
async def handle_conference_date(message: types.Message, state: FSMContext):
    text = message.text.strip()
    # Проверка формата ДД.ММ.ГГГГ
    if re.match(date_pattern, text):
        # Получаем введенную дату
        date = text
        parsed_date = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        print(f"Дата для конференции: {date}")

        data = {
            'date': f"{formatted_date}T00:00:00Z",
            'limUp': f"{formatted_date}T12:00:00Z",
            'limLow': f"{formatted_date}T18:00:00Z"
            }
        resp = {
            'times': [],
        }
        json_data = json.dumps(data)
        header = {
            'Content-Type': 'application/json'
        }
        response = requests.get('http://localhost:8082/checkDate', headers=header, data=json_data)

        respData = response.json().get('times')
        possible_times = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        times = ""
        timesList = []
        # for timestamp in respData:
        #     output += f"{timestamp}\n"
        print(respData)
        if respData == None:
            freeTimes = possible_times
            print(freeTimes)
        else:
            for timestamp in respData:
                time_part = timestamp.split('T')[1][:5]  # Извлекаем время и оставляем первые 5 символов (часы и минуты)
                timesList.append(time_part)
                times += time_part
                # times += f"{time_part}\n"

            freeTimes = possible_times
            print(times)
            for time in timesList:
                if time in possible_times:
                    freeTimes.remove(time)
            print(freeTimes)

        if len(freeTimes) != 0:
            # Сохраняем дату в состояние для дальнейшего использования
            await state.update_data(date=date)

            # Создаем строку с доступными временами
            time_options = "\n".join(freeTimes)

            # Запрашиваем у пользователя выбрать время
            await message.reply(f"Вы выбрали дату: {date}. Теперь выберите время из доступных:\n{time_options}\n и введите в формате \"ЧЧ:ММ Фамилия Имя Отчество\"", reply_markup=menu_menu)

            # Переходим в состояние ожидания времени
            await state.set_state(Form.waiting_for_time)
        else:
            await message.reply("Извините, но на выбранную вами дату нет свободных мест", reply_markup=menu_menu)

    elif re.match(menu_pattern, text):
        await message.reply("Вы вернулись в главное меню.", reply_markup=main_menu)

    else:
        # Если формат неверный
        await message.reply("Неверный формат. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ", reply_markup=menu_menu)

# Обработчик получения времени время ЧЧ:ММ
@dp.message(F.text, Form.waiting_for_time)
async def handle_conference_time(message: types.Message, state: FSMContext):
    # Проверка формата ЧЧ:ММ (время)
    text = message.text.strip()
    match = re.match(time_pattern, message.text.strip())
    print(match)
    if match:
        time, lastname, firstname, midname = match.group('time', 'midname', 'firstname', 'lastname')
        print(time)
        print(lastname)
        print(firstname)
        print(midname)
        selected_time = time

        # print(f"Вы выбрали время: {selected_time}, {name}")s

        # Получаем дату из состояния
        user_data = await state.get_data()
        date = user_data.get("date")
        parsed_date = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        timeUTC = f"{formatted_date}T{time}:00Z"
        service_name = user_data.get("service_name")

        # Подтверждаем выбор времени и даты
        await message.reply(f"Вы выбрали время: {selected_time} на {date}. Мы продолжаем {firstname} {midname} {lastname}", reply_markup=menu_menu)

        data = {
            'date': timeUTC,
            'firstName': firstname,
            'midName': midname,
            'lastName': lastname,
            'service': service_name,
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
                # Отправляем информацию администратору
        user_account_info = f"Новая запись:\n" \
                            f"Пользователь: {message.from_user.full_name}\n" \
                            f"Username: @{message.from_user.username}\n" \
                            f"ID: {message.from_user.id}\n" \
                            f"Услуга: {service_name}\n" \
                            f"Дата: {date}\n" \
                            f"Время: {selected_time}"

        # Отправляем информацию администратору
        await bot.send_message(MyID, user_account_info)
        await state.clear()
        # Закрываем состояние, так как процесс завершен
    elif re.match(menu_pattern, text):
        await message.reply("Вы вернулись в главное меню.", reply_markup=main_menu)
    else:
        # Если формат неверный
        await message.reply("Неверный формат. Пожалуйста, время в формате ЧЧ:ММ.", reply_markup=menu_menu)





# Обработчик кнопки "Меню"
@dp.message(F.text == "Меню")
async def go_to_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_menu)

# Обработчик команды /appointments
@dp.message(Command("appointments"))
async def start_command(message: types.Message):

    data = {}
    json_data = json.dumps(data)
    header = {
        'Content-Type': 'application/json'
    }
    response = requests.get('http://localhost:8082/getAppointments', headers=header, data=json_data)

    respData = response.json().get('appointments')

    # Перебираем пользователей и формируем строки
    results = []
    for user in respData:
        lines = []
        for key, value in user.items():
            lines.append(f'{key}: {value}')
        results.append('\n'.join(lines))

    # Объединяем строки для всех пользователей с разделителем '\n\n'
    final_result = '\n\n'.join(results)
    await bot.send_message(MyID, final_result)



async def main():
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
