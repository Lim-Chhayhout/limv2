import requests

def send_video(token, chat_id, video_url, caption):
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    payload = {
        "chat_id": chat_id,
        "video": video_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    return requests.post(url, data=payload).json()
