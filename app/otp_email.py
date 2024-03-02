import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, status

from pydantic import EmailStr


def send_email(to_email: EmailStr, otp_code: str):
    try:
        # Set up the email server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("jobayer0001@std.bdu.ac.bd", os.getenv("GMAIL_APP_PASSWORD"))

        # msg = f"your otp is {otp_code}"

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = "jobayer0001@std.bdu.ac.bd"
        msg['To'] = to_email
        msg['Subject'] = "OTP code for project app"
        msg.attach(MIMEText(f"Your OTP code is: {otp_code}", 'plain'))

        # Send the email
        server.sendmail("jobayer0001@std.bdu.ac.bd", to_email, msg.as_string())
    except (smtplib.SMTPException, ConnectionRefusedError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"email was wrong: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    finally:
        server.quit()

if __name__ == "__main__":
    send_email("jobama2002@gmail.com", "1024")
