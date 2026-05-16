from flask import current_app
from models import db, Notification


def create_notification(user, title, message, link=None):
    notification = Notification(user=user, title=title, message=message, link=link)
    db.session.add(notification)
    return notification


def send_email_notification(user, subject, body):
    if not user.email_notifications:
        return False
    if not current_app.config.get('MAIL_ENABLED'):
        print(f'[WorkNet Email] To: {user.email} | {subject}\n{body}')
        return True
    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body, 'plain')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = user.email
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            if current_app.config['MAIL_USERNAME']:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f'[WorkNet Email Error] {exc}')
        return False


def notify_user(user, title, message, link=None, email=False):
    create_notification(user, title, message, link)
    if email:
        send_email_notification(user, title, message)
