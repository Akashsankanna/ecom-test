import requests
from app.core.config import settings

def send_sms(phone: str, otp: str):
    url = "https://api.msg91.com/api/v5/flow/"

    payload = {
        "flow_id": settings.SMS_FLOW_ID,
        "sender": "MEDAPP",
        "mobiles": f"91{phone}",
        "OTP": otp
    }

    headers = {
        "authkey": settings.SMS_API_KEY,
        "Content-Type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception("SMS failed")
    
