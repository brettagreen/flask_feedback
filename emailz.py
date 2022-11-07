from sendgrid import SendGridAPIClient
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_pw_email(recipient, URLtoken):
    #sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDGRID_API_SENDER'))
    to_email = To(recipient)
    subject = 'password reset link'
    content = Content('text/plain', URLtoken)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    print('API KEY', os.environ.get('SENDGRID_API_KEY'))
    print('FROM EMAIL', os.environ.get('SENDGRID_API_SENDER'))
    print('TO EMAIL', recipient)
    print('URL TOKEN', URLtoken)

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print('STATUS CODE', response.status_code)
    print('RESPONSE HEADERS', response.headers)
