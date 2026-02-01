import requests

def send_text(token, chat_id, html_txt):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": html_txt,
        "parse_mode": "HTML"
    }
    return requests.post(url, data=payload).json()
