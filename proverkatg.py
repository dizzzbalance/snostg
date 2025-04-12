import requests

url = "https://telegram.org/support"
data = {
    "email": "example@example.com",
    "message": "Тестовая жалоба"
}

response = requests.post(url, data=data)
print(f"Статус-код: {response.status_code}")
print(f"Ответ: {response.text}")