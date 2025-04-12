from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

def run_with_tor():
    tor_proxy = "127.0.0.1:9050"
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'socksProxy': tor_proxy,
        'socksVersion': 5,
    })

    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Запуск без графического интерфейса
    firefox_options.proxy = proxy  # Установка прокси для Tor

    # Локальное подключение к Firefox
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def run_without_tor():
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Запуск без графического интерфейса

    # Локальное подключение к Firefox
    driver = webdriver.Firefox(options=firefox_options)
    return driver

try:
    print("Попытка запуска через Tor...")
    driver = run_with_tor()
    driver.get("https://check.torproject.org")
    print("Страница открыта:", driver.title)
except Exception as e:
    print(f"Ошибка при использовании Tor: {e}. Переключение на обычный Firefox...")
    driver.quit()
    driver = run_without_tor()
    driver.get("https://example.com")
    print("Страница открыта без Tor:", driver.title)
finally:
    driver.quit()