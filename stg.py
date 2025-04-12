import random
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, Style
from faker import Faker
import os
import re

fake = Faker("ru_RU")

# Типы жалоб и их тексты
complaint_types = {
    1: {"name": "Спам", "texts": [
        "Пользователь {user} ID: {user_id} использует чат для рассылки рекламы и спама, что нарушает правила сообщества. Прошу удалить его сессию и заблокировать возможность отправки нежелательных сообщений.",
        "Здравствуйте, хочу пожаловаться на {user} ID: {user_id}, он использует спам для продвижения своего канала из-за чего невозможно общаться в группе, прошу принять меры по удалению аккаунта. Спасибо",
        "Доброго времени суток, прошу принять меры по рассылке спама. ID: {user_id} пользователя.",
    ]},
    2: {"name": "Порнография", "texts": [
        "Добрый день, прошу заблокировать доступ к порнографическому контенту. Акаунту {user} с  ID: {user_id}. Проблема в том что он занимается продажей детской порнографии",
        "Здравствуйте, хочу подать жалобу на порнографию. Пользователь {user} с  ID: {user_id} продает детскую порнографию, прошу принять меры по удалению акаунта. Спасибо",
        "Данный пользователь {user} с ID: {user_id} распространяет запрещённый детский контент. Прошу вас удалить данный аккаунт. Спасибо",
    ]},
    3: {"name": "Фишинг", "texts": [
        "Здравствуйте, сообщаю о подозрительной попытке фишинга. Акк: {user} ID: {user_id}.",
        "Добрый день, прошу обратить внимание на пользователя {user} с ID: {user_id}, он создает фишинговые ссылки, прошу принять меры по удалению данного аккаунта.",
        "Жалоба на фишинг. Пожалуйста, примите меры. {user} с ID: {user_id} использует фишинг для получения личных данных других пользователей, прошу принять меры по удалению аккаунта. Спасибо",
    ]},
    4: {"name": "Дианон", "texts": [
        "Здравствуйте, хочу пожаловаться на пользователя {user} с ID:{user_id}, он нарушает правила Telegram, продаёт услуги деанона и занимается терроризмом.",
        "Пользователь {user} с ID: {user_id} угрожает деанонимизацией и сватингом. Требую удалить его аккаунт для безопасности других пользователей.",
        "Данный пользователь {user} с ID: {user_id} угрожает мне доксингом и сватингом. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопасности.",
    ]},
    5: {"name": "Мошенничество", "texts": [
        "Уважаемая служба поддержки! Хочу сообщить о случае мошенничества. Пользователь {user} с ID: {user_id} пишет людям и предлагает услугу по выводу Notcoin на карту. После перевода Notcoin пользователь добавляет в чёрный список и отказывается переводить Notcoin. Прошу принять меры по удалению аккаунта. Спасибо!",
        "Добрый день! Прошу рассмотреть жалобу на мошенничество. Пользователь {user} с ID: {user_id} занимается мошенничеством, прошу принять меры по блокировке аккаунта.",
        "Обращаюсь к вам с жалобой на пользователя {user} с ID: {user_id}. Данный пользователь обманным путём получил от меня Notcoin, пообещав вывод на карту, но после получения средств заблокировал меня. Прошу принять меры и вернуть мои средства.",
    ]},
}

def log_status(message):
    """Логирует статус отправки жалоб."""
    try:
        with open("status_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")
    except IOError as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка записи в лог: {e}")

def verify_tor():
    """Проверяет, что запросы проходят через Tor."""
    try:
        response = requests.get("https://httpbin.org/ip", proxies={
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }, timeout=20)
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Ваш IP через Tor: {response.json()['origin']}")
    except requests.RequestException as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка проверки Tor: {e}")
        log_status(f"Ошибка проверки Tor: {e}")
        exit(1)

def setup_selenium_with_tor():
    """Настройка Selenium для работы через Tor."""
    tor_proxy = "127.0.0.1:9050"
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'socksProxy': tor_proxy,
        'socksVersion': 5,
    })

    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Запуск без графического интерфейса
    firefox_options.set_preference("media.peerconnection.enabled", False)  # Отключение WebRTC
    firefox_options.set_preference("media.navigator.enabled", False)

    try:
        driver = webdriver.Firefox(options=firefox_options)
        return driver
    except WebDriverException as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка запуска Selenium: {e}")
        log_status(f"Ошибка запуска Selenium: {e}")
        exit(1)

def send_to_telegram_support_selenium(data, complaint_text):
    """Отправляет жалобу через сайт поддержки Telegram с использованием Selenium."""
    driver = None
    try:
        driver = setup_selenium_with_tor()
        driver.get("https://telegram.org/support")
        print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Открыта страница: {driver.title}")

        # Ожидание элемента формы
        try:
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "complaint"))
            )
            input_field.send_keys(complaint_text)
            input_field.send_keys(Keys.RETURN)
            print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Жалоба успешно отправлена через Selenium.")
            log_status("Жалоба успешно отправлена через Selenium.")
        except TimeoutException:
            print(f"[{Fore.RED}-{Style.RESET_ALL}] Элемент формы не найден.")
            log_status("Элемент формы не найден.")
    except WebDriverException as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка при отправке через Selenium: {e}")
        log_status(f"Ошибка при отправке через Selenium: {e}")
    finally:
        if driver:
            driver.quit()

def send_requests(data):
    """Отправляет жалобы через Selenium."""
    for i in range(data["request_count"]):
        complaint_text = random.choice(complaint_types[data["complaint_type"]]["texts"]).format(
            user=data["username"],
            user_id=data["user_id"] or "не указан",
            violation_link=data["violation_link"] or "не указана"
        )
        print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Отправка жалобы {i + 1}...")
        send_to_telegram_support_selenium(data, complaint_text)
def validate_username(username):
    """Проверяет и форматирует юзернейм."""
    if not username.startswith("@"):
        username = "@" + username
    if not re.match(r"^@[A-Za-z0-9_]+$", username):
        raise ValueError("Юзернейм может содержать только латинские буквы, цифры и символ '_', и должен начинаться с '@'.")
    return username

def validate_user_id(user_id):
    """Проверяет, что ID состоит только из чисел или пустой."""
    if user_id and not user_id.isdigit():
        raise ValueError("ID может содержать только числа или быть пустым.")
    return user_id

def get_user_input():
    """Запрашивает данные у пользователя."""
    try:
        print("Выберите тип жалобы:")
        for key, value in complaint_types.items():
            print(f"{key}. {value['name']}")
        
        complaint_type = int(input("Введите номер типа жалобы: ").strip())
        if complaint_type not in complaint_types:
            raise ValueError("Неверный номер типа жалобы.")
        
        request_count = int(input("Введите количество запросов: ").strip())
        if request_count <= 0:
            raise ValueError("Количество запросов должно быть больше 0.")

        username = input("Введите юзернейм (например, @username): ").strip()
        username = validate_username(username)

        user_id = input("Введите ID пользователя (можно пропустить): ").strip()
        user_id = validate_user_id(user_id)

        violation_link = input("Введите ссылку на нарушение (можно пропустить): ").strip()

        return {
            "complaint_type": complaint_type,
            "request_count": request_count,
            "username": username,
            "user_id": user_id,
            "violation_link": violation_link,
        }
    except ValueError as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка ввода: {e}")
        log_status(f"Ошибка ввода: {e}")
        return None
    
def main():
    """Основная логика программы."""
    try:
        print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Программа для отправки жалоб запущена.")
        
        # Проверка анонимности через Tor
        verify_tor()
        
        data = get_user_input()
        if data is None:
            print(f"[{Fore.RED}-{Style.RESET_ALL}] Программа завершена из-за ошибки ввода.")
            return

        print(f"[INFO] Начинаем отправку {data['request_count']} жалоб типа '{complaint_types[data['complaint_type']]['name']}'...")
        send_requests(data)
        print(f"[{Fore.MAGENTA}+{Style.RESET_ALL}] Все жалобы успешно отправлены!")
    except KeyboardInterrupt:
        print(f"\n[{Fore.RED}-{Style.RESET_ALL}] Программа была прервана пользователем.")
        log_status("Программа была прервана пользователем.")

if __name__ == "__main__":
    main()