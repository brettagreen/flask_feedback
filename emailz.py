import smtplib
from email.message import EmailMessage

def send_pw_email(email, URLtoken):
    msg = EmailMessage()
    msg.set_content(URLtoken)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'password reset link'
    msg['From'] = 'admin@flaskfeedback.com'
    msg['To'] = email

    # Send the message via our own SMTP server.
    print('-----------------------------')
    print('getting here, before localhost')
    s = smtplib.SMTP('localhost:5000', 1025)
    s.send_message(msg)
    print('-----------------------------')
    print('getting here, after localhost')
    s.quit()