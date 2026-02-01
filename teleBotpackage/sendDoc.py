import requests

def send_doc(token, chat_id, doc_url, caption):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    payload = {
        "chat_id": chat_id,
        "document": doc_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    return requests.post(url, data=payload).json()
