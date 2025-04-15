import random
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException, StaleElementReferenceException
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
        "Жалоба на рассылку рекламы. Пользователь {user} с ID: {user_id} спамит по группам, прошу принять меры",
        "Hello, I want to complain about ID: {user_id}, he uses spam to promote his channel, which makes it impossible to communicate in the group, please take steps to delete the account. Thank you",
        "Good day, I ask you to take measures to send spam. ID: {user_id} of the user.",
        "Complaint about sending advertisements. User with ID: {user_id} is spamming groups, please take action",
        "Доброго времени суток, прошу принять меры по рассылке спама. ID: {user_id} пользователя.",
    ]},
    2: {"name": "Порнография", "texts": [
     "Добрый день, прошу заблокировать доступ к порнографическому контенту. Акаунту {user} с  ID: {user_id}. Проблема в том что он занимается продажей детской порнографией",
        "Здравствуйте, хочу подать жалобу на порнографию.  Пользиватель {user} с  ID: {user_id} продает детскую порнографию, прошу принять меры по удалению акаунта. Спасибо",
        "Данный пользиватель {user} с ID: {user_id} растространяет запрешеный детский контент (дп,цп) прошу вас удалить данный акаунт. Спасибо",
        "Good afternoon, please block access to pornographic content. Account with ID: {user_id}. The problem is that it sells child pornography",
         "Hello, I want to file a complaint about pornography. User ID: {user_id} sells child pornography, please take steps to delete the account. Thank you",
         "This user with ID: {user_id} distributes prohibited children's content (dp, cp), I ask you to delete this account. Thank you",
         "Пользователь {user_id} распространяет порнографические материалы. Прошу заблокировать его аккаунт за нарушение правил платформы. Ссылка на материалы: {user_id}",
                "Обнаружено распространение порнографии пользователем {user_id}. Прошу принять меры. Ссылка на материалы: {user_id}",
                "Добрый день, прошу заблокировать аккаунт с  ID: {user_id}. Проблема в том,что он занимается продажей детской порнографией, вот ссылка на нарушение: {user_id}",
                "Здравствуйте, хочу подать жалобу на порнографию.  Пользователь с  ID: {user_id} продает детскую порнографию,вот ссылка на нарушение:{user_id},прошу принять меры по удалению акаунта. Спасибо",
                "Данный пользователь с ID: {user_id} растространяет запрещеный детский контент (дп,цп) прошу вас удалить данный акаунт.Также ссылка на нарушение:{user_id}.Спасибо",
                "Добрый день, прошу заблокировать аккунт с айди: {user_id} за распространение порнографии, точнее этот человек размещает порнографию, а также детскую порнографию в чатах ({user_id}) и так далее, что может повлиять на психику людей, которые находятся в этих чатах, а также это нарушает вашу политику, прошу заблокировать данного человека, также на момент жалобы у этого человека на аватарке было неприличное фото, поэтому прошу вас отреагировать на это быстро и четко. Заранее спасибо!",
                         "Hello, I want to file a complaint about pornography. User with ID: {user_id} sells child pornography,link to violation: {user_id},please take steps to delete the account. Thank you",
                "Good afternoon, please block the account with ID: {user_id}. The problem is that he is selling child pornography.Link to violation: {violation_link}.",
                "This user with ID: {user_id} distributes prohibited children's content (dp, cp),and link to violation: {user_id},I ask you to delete this account. Thank you",
                "Good afternoon, I ask you to block the account with ID: {user_id} for distributing pornography, more precisely, this person posts pornography, as well as child pornography in chats and so on,link to violation: {user_id},which can affect the psyche of people who are in these chats, and also violates your policy, I ask you to block this person, also at the time of the complaint this person had an indecent photo on his avatar, so I ask you to respond to this quickly and clearly. Thank you in advance!",
    ]},
    3: {"name": "Фишинг", "texts": [
        "Здравствуйте, сообщаю о подозрительной попытке фишинга. Акк: {user} ID: {user_id}.",
        "Добрый день, прошу обратить внимание на пользивателя {user} с ID: {user_id} он создает фишинг сылки, прошу принять меры по удалению данного акаунта",
        "Жалоба на фишинг. Пожалуйста, примите меры. {user} с ID: {user_id} использует фишинг для получения личных данных других пользывателей, прошу принять меры по удалению акаунта. Спасибо",
        "Hello, I'm reporting a suspicious phishing attempt. ID: {user_id}.",
         "Good afternoon, please pay attention to the user with ID: {user_id}, he creates phishing links, please take measures to delete this account",
         "Phishing complaint. Please take action. ID: {user_id} uses phishing to obtain personal information of other users, please take action to delete the account. Thank you",
    ]},
    4: {"name": "Дианон", "texts": [
       "Здравствуйте уважаемая поддержка телеграмм,хочу пожаловаться на пользователя {user} с ID:{user_id} дело в том что он нарушает правила телеграмм, он продает услули деанона, занимается терроризмом , а еще хочу сообщить что он оскорбляет чужие личности! ",
    "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с ID: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
    "Telegram, деактивируйте аккаунт {user} с ID: {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
    "Данный пользователь {user} с ID: {user_id}, угрожает мне д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности",
    "Telegram, деактивируйте аккаунт {user}, Id:  {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
    "Данный пользователь {user}, id: {user_id}, угрожает мне     д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности.",
       "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с id: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
       "Привествую Вас. Я являюсь родителем моего ребёнка и ему поступют угрозы об сливе данных с данного аккаунта {user}, id:{user_id}. Прошу удалить его аккаунт, так как теперь у моего ребёнка нарушена психика!",
       "Мне сказали, что телеграм самый безопасный мессенджер, только сейчас этот пользователь {user} id: {user_id} хочет слить мои данные.",
       "Hello, dear telegram moderator, I want to complain to you about a channel that sells doxing and swatting services ID: {user_id}, I ask you to take measures to delete the account.",
         "Good day, I ask you to take action on my complaint. The telegram user under ID: {user_id} is engaged in selling the services of Doxing and Swatting, I ask you to take action. Thank you.",
         "This account under ID: {user_id} is engaged in doxing and swatting, please take measures to delete the account.",
    ]},
    5: {"name": "Мошенничество", "texts": [
        "Уважаемая служба поддержки!Хочу сообщить о случае мошенничества. Пользователь {user} с ID: {user_id} пишет людям и предлагает услугу по выводу Notcoin на карту. После перевода Notcoin пользователь добавляет в черный список и отказывается переводить Notcoin. Прошу принять меры по удалению аккаунта. Спасибо!",
    "Добрый день!Прошу рассмотреть жалобу на мошенничество. Пользователь {user} с ID: {user_id} занимается мошенничеством, прошу принять меры по блокировке аккаунта.",
    "Обращаюсь к вам с жалобой на пользователя {user} с ID: {user_id}. Данный пользователь обманным путем получил от меня Notcoin, пообещав вывод на карту, но после получения средств заблокировал меня. Прошу принять меры и вернуть мои средства.",
    "Прошу обратить внимание на действия пользователя {user} с ID: {user_id}.Он предлагает услуги по выводу Notcoin, но после получения оплаты отказывается выполнять свои обязательства и блокирует пользователей. Это мошенник!",
    "ВНИМАНИЕ! Мошенник!Пользователь {user} с ID: {user_id} обманывает людей, предлагая несуществующие услуги. Будьте бдительны и не переводите ему свои средства!",
    "Я стал жертвой мошенничества со стороны пользователя {user} с ID: {user_id}.Прошу принять меры по блокировке его аккаунта и возврату моих средств.",
    "Требую наказать мошенника {user} с ID: {user_id}!Он обманул меня и многих других пользователей. Прошу принять меры!",
    "Обращаюсь к вам с просьбой о помощи.Пользователь {user} с ID: {user_id} обманным путем завладел моими средствами. Прошу вернуть мои Notcoin и заблокировать мошенника.",
    "Сколько можно терпеть мошенников на вашей платформе? Пользователь с ID: {user_id} продолжает обманывать людей. Прошу принять срочные меры!",
    "Dear support service, I want to report a case of fraud. A user with ID: {user_id} writes to people and offers a service to help them withdraw notcoin to a card. After transferring the notcoin, the user is blacklisted and refuses to transfer the notcoin, I ask you to take measures to delete the account.  Thank you",
         "Good afternoon, I ask you to consider a complaint about fraud. The user with ID: {user_id} is engaged in fraud, I ask you to take measures to assign the account.",
         "Fraud complaint against user ID: {user_id}. Please take action.",
    ]},
}

def log_status(message):
    """
    Логирует статус отправки жалоб.
    """
    try:
        with open("status_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")
    except IOError as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка записи в лог: {e}")

def verify_tor():
    """
    Проверяет, что запросы проходят через Tor.
    """
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
    """
    Настройка Selenium для работы через Tor.
    """
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
    """
    Отправляет жалобу через сайт поддержки Telegram с использованием Selenium.
    """
    driver = None
    try:
        driver = setup_selenium_with_tor()
        driver.get("https://telegram.org/support?setln=ru")
        print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Открыта страница: {driver.title}")

        # Ожидание полей формы
        try:
            # Генерация фейковых данных для ФИО и электронной почты с использованием Faker
            fake_name = fake.name()  # Фейковое ФИО
            fake_email = fake.email()  # Фейковая электронная почта

            # Заполняем поле "ФИО"
            legal_name_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "legal_name"))  # Используем name="legal_name"
            )
            legal_name_field.send_keys(fake_name)

            # Заполняем поле "E-mail"
            email_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))  # Используем name="email"
            )
            email_field.send_keys(fake_email)

            # Заполняем поле "Текст жалобы"
            message_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "message"))  # Используем name="message"
            )
            message_field.send_keys(complaint_text)
            
            # Сохраняем скриншот после заполнения всех полей
            filled_fields_screenshot = os.path.join(os.getcwd(), "filled_fields_screenshot.png")
            driver.save_screenshot(filled_fields_screenshot)
            print(f"[INFO] Скриншот после заполнения полей сохранён: {filled_fields_screenshot}")

            # Находим кнопку "Отправить" по классу
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
            )
            
            # Нажимаем на кнопку
            try:
                submit_button.click()
                print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Жалоба успешно отправлена через Selenium.")
            except StaleElementReferenceException:
                print(f"[{Fore.RED}-{Style.RESET_ALL}] Кнопка 'Отправить' стала недействительной. Повторный поиск...")
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
                )
                submit_button.click()
            except TimeoutException:
                print(f"[{Fore.RED}-{Style.RESET_ALL}] Кнопка 'Отправить' не найдена.")

            # Сохраняем скриншот после отправки жалобы
            submitted_screenshot = os.path.join(os.getcwd(), "submitted_screenshot.png")
            driver.save_screenshot(submitted_screenshot)
            print(f"[INFO] Скриншот после отправки жалобы сохранён: {submitted_screenshot}")
            log_status("Жалоба успешно отправлена через Selenium.")

        except TimeoutException:
            # Сохранение HTML страницы для диагностики
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[{Fore.RED}-{Style.RESET_ALL}] Поля формы не найдены. Проверьте страницу.")
            log_status("Поля формы не найдены. Проверьте страницу.")
            
            # Сохранение скриншота страницы
            screenshot_path = "screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Скриншот сохранён: {screenshot_path}")
            
            # Запись всех доступных элементов на странице
            all_elements = driver.find_elements(By.XPATH, "//*")
            with open("elements_log.txt", "w", encoding="utf-8") as f:
                for element in all_elements:
                    f.write(f"Tag: {element.tag_name}, Attributes: {element.get_attribute('outerHTML')}\n")
            print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Все элементы страницы сохранены в 'elements_log.txt'.")
    except WebDriverException as e:
        print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка при отправке через Selenium: {e}")
        log_status(f"Ошибка при отправке через Selenium: {e}")
    finally:
        if driver:
            driver.quit()

def send_requests(data):
    """
    Отправляет жалобы через Selenium.
    """
    for i in range(data["request_count"]):
        try:
            # Проверяем, что все необходимые ключи существуют
            if "complaint_type" not in data or "username" not in data:
                raise KeyError("Отсутствует обязательный ключ в данных")

            # Подставляем значения
            complaint_type = data.get("complaint_type")
            user_id = data.get("user_id", None)  # None, если user_id отсутствует
            username = data.get("username", "Не указано")
            violation_link = data.get("violation_link", "Не указана")

            # Проверяем, что complaint_type существует в словаре complaint_types
            if complaint_type not in complaint_types:
                raise KeyError(f"Некорректный complaint_type: {complaint_type}")

            # Формируем текст жалобы
            complaint_template = random.choice(complaint_types[complaint_type]["texts"])
            if user_id:
                complaint_text = complaint_template.format(
                user=data["username"],
                user_id=data["user_id"] or "не указан",
                violation_link=data["violation_link"] or "не указана"
                )
            else:
                # Если user_id отсутствует, формируем текст без него
                complaint_text = complaint_template.replace("{user_id}", "").format(
                    user=username,
                    violation_link=violation_link,
                )
                print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Внимание: ID пользователя отсутствует. Он не будет включён в жалобу.")

            print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Отправка жалобы {i + 1}...")
            send_to_telegram_support_selenium(data, complaint_text)
        except KeyError as e:
            print(f"[{Fore.RED}-{Style.RESET_ALL}] Ошибка: отсутствует ключ {e} в данных.")
            log_status(f"Ошибка: отсутствует ключ {e} в данных.")
        except Exception as e:
            print(f"[{Fore.RED}-{Style.RESET_ALL}] Непредвиденная ошибка: {e}")
            log_status(f"Непредвиденная ошибка: {e}")
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
         "user_id": user_id or "не указан",
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
