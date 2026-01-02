import os
import time
import uuid


def generate_token():
    return str(uuid.uuid4())

def clean_old_temp_files(folder, request=None, max_age=3600):
    now = time.time()
    for filename in os.listdir(folder):
        if filename.startswith('cover_') or filename.startswith('image_'):
            try:
                ts = int(filename.split('_')[1])
            except ValueError:
                continue

            if now - ts > max_age:
                path = os.path.join(folder, filename)
                if os.path.exists(path):
                    os.remove(path)

                if request:
                    cover_path = request.session.get('cover_temp_path')

                    if cover_path == filename:
                        del request.session['cover_temp_path']
                        del request.session['cover_url']

                    images         = request.session.get('images', [])
                    cleaned_images = []

                    for image in images:
                        if image['path'] != filename:
                            cleaned_images.append(image)

                    request.session['images'] = cleaned_images