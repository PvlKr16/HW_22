import os
import smtplib
import redis
from flask import jsonify
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from config import SMTP_HOST, SMTP_PORT, SMTP_PASSWORD, SMTP_USER

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def send_email(order_id: str, receiver: str, filename: str):
    """
    Отправляет пользователю `receiver` письмо по заказу `order_id` с приложенным файлом `filename`

    Вы можете изменить логику работы данной функции
    """
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        email = MIMEMultipart()
        email['Subject'] = f'Изображения. Заказ №{order_id}'
        email['From'] = SMTP_USER
        email['To'] = receiver

        with open(os.path.join(f'src_files/{order_id}/', filename), 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={filename}'
        )
        email.attach(part)
        text = email.as_string()

        server.sendmail(SMTP_USER, receiver, text)
        # os.remove(filename)


def add_email(receiver: str):
    if receiver in r.smembers('subscribers'):
        return 'Email already exists', 404
    else:
        r.sadd('subscribers', receiver)
        return jsonify('Successfully subscribed'), 200


def remove_email(receiver: str):
    if receiver not in r.smembers('subscribers'):
        return jsonify({'error': 'Email already unsubscribed'}), 404
    else:
        r.srem('subscribers', receiver)
        return jsonify('Successfully unsubscribed'), 200
