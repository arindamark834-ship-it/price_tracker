import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "arindamark834@gmail.com"      # Replace with your email
SENDER_PASSWORD = "arindamark8#"      # Replace with your Gmail App Password
RECEIVER_EMAIL = "arindamark834@gmail.com"    # Email address to receive alerts

def send_price_drop_alert(product_title: str, old_price: float, new_price: float, url: str):
    msg = EmailMessage()
    msg['Subject'] = f"🚨 Price Drop Alert: {product_title}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    body = (
        f"Great news! The price for '{product_title}' has dropped.\n\n"
        f"Previous Price: ${old_price:.2f}\n"
        f"New Price: ${new_price:.2f}\n\n"
        f"Product Link: {url}"
    )
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"[Notifier] Email alert sent for '{product_title}'!")
    except Exception as e:
        print(f"[Notifier] Failed to send email: {e}")