from celery import Celery

from image import blur_image_new
from mail import send_email
from celery.schedules import crontab


celery = Celery(
    'celery_',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    broker_connection_retry_on_startup=True
)


@celery.task
def process_image(order, src_filename):
    blur_image_new(order=order, src_filename=src_filename)
    # return f'File {src_filename} blurred'
    print(order)
    return order


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:
    if isinstance(sender, Celery):
        sender.add_periodic_task(10, send_files.s(kwargs['kwargs']['receiver']))
        sender.add_periodic_task(
            crontab(hour='8', minute='30', day_of_week='1'),
            send_files.s(kwargs['receiver'])
        )


@celery.task
def send_files(order: str, receiver: str, filename: str) -> tuple[str, int]:
    send_email(order_id=order, receiver=receiver, filename=filename)
    return 'OK', 200


@celery.task
def subscribe_user(receiver: str) -> tuple[str, int]:
    return f'Add user {receiver} to subscribers', 200


@celery.task
def unsubscribe_user(receiver: str) -> tuple[str, int]:
    return f'Delete user {receiver} from subscribers processed', 200
