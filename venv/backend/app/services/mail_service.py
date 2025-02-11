import smtplib
from email.mime.text import MIMEText

def send_token_email(to_email, token):
    # Email configuration
    sender_email = 'your-email@gmail.com'
    sender_password = 'your-email-password'
    subject = 'Your Purchased Token'
    body = f'Your token is: {token}'

    # Create the email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')