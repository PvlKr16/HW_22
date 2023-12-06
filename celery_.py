from celery import Celery

from image import blur_image_new
from mail import send_email
from celery.schedules import crontab


celery_app = Celery(
    'celery_',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    broker_connection_retry_on_startup=True
)


@celery_app.task
def process_image(order, receiver, src_filename):
    blur_image_new(order=order, src_filename=src_filename)
    return order, receiver, src_filename


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:
    if isinstance(sender, Celery):
        sender.add_periodic_task(10, send_files.s(kwargs['kwargs']['receiver']))
        sender.add_periodic_task(
            crontab(hour='8', minute='30', day_of_week='1'),
            send_files.s(kwargs['receiver'])
        )


@celery_app.task
def send_files(data: tuple[str, int], message):  # данные приходят кортежем, поэтому тут указываем один параметр...
    order, receiver, filename = data  # ...а тут делаем распаковку кортежа
    print(message)
    send_email(order_id=order, receiver=receiver, filename=filename)
    return 'OK', 200


@celery_app.task
def subscribe_user(receiver: str) -> tuple[str, int]:
    return f'Add user {receiver} to subscribers', 200


@celery_app.task
def unsubscribe_user(receiver: str) -> tuple[str, int]:
    return f'Delete user {receiver} from subscribers processed', 200
