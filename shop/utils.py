import uuid
import time
import os

def generate_order_id():
    return f'ORD-{uuid.uuid4().hex[:10].upper()}'

def clean_old_temp_files(folder, request=None, max_age=3600):
    now = time.time()
    for filename in os.listdir(folder):
        if filename.startswith('Book-cover_'):
            try:
                ts = int(filename.split('_')[1])
            except ValueError:
                continue

            if now - ts > max_age:
                path = os.path.join(folder, filename)
                if os.path.exists(path):
                    os.remove(path)

                if request:
                    cover_path = request.session.get('book_cover_temp_path')

                    if cover_path == filename:
                        del request.session['book_cover_temp_path']
                        del request.session['book_cover_url']