import os
import random
from flask import Flask, request, jsonify
from celery import group, chain
from werkzeug.utils import secure_filename

from celery_ import celery, process_image, send_files, subscribe_user, unsubscribe_user
from mail import add_email, remove_email


app = Flask(__name__)
app.config.update(
    DEBUG=True,
    WTF_CSRF_ENABLED=False,
)


@app.route('/blur/<receiver>', methods=['POST'])
def process_images(receiver):

    filenames = [name for name in request.files]
    order = str(random.randint(1, 1000))
    os.mkdir(f'src_files/{order}/')
    results = dict()
    for filename in filenames:
        file = request.files.get(filename)
        file.save(os.path.join(f'src_files/{order}/', secure_filename(f'{file.filename}')))
    counter = 1
    for file in os.listdir(f'src_files/{order}/'):
        task1 = process_image.s(order=order, src_filename=file)
        task2 = send_files.s(order=order, receiver=receiver, filename=file)
        task_chain = chain(task1 | task2)
        result = task_chain.apply_async()
        results[f'{order}_{counter}'] = result.id
        counter += 1

    return jsonify(results), 202


@app.route('/status/<result_id>', methods=['GET'])
def get_group_status(result_id):
    result = celery.GroupResult.restore(result_id)  # <class 'celery.result.GroupResult'>
    if result:
        status = result.completed_count() / len(result)
        if status < 1.0:
            return jsonify({'in process': f'{status*100}% complete'}), 200
        elif status == 1.0:
            return jsonify({'status': status}), 200
    else:
        return jsonify({'error': 'Invalid group_id'}), 404


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    email = request.form.get('email')
    subscribe_user.s(email).apply_async()
    return add_email(email)


@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    email = request.form.get('email')
    unsubscribe_user.s(email).apply_async()
    return remove_email(email)


"""
celery -A app.celery worker --loglevel=info
celery -A app.celery flower
celery -A celery_ beat
"""

if __name__ == '__main__':
    app.run(debug=True)
