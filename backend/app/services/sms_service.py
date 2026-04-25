from app.integrations.sms_client import send_sms

def send_signup_otp(phone: str, otp: str):
    message = f"Your OTP is {otp}. Valid for 5 minutes."
    send_sms(phone, message)