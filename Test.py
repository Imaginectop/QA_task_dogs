import os
import requests
import logging
from urllib.parse import urlparse
import pytest

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YaUploader:
    def __init__(self, token):
        if not token:
            raise ValueError("Yandex Disk token is required.")
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, path):
        response = requests.put(f'{self.base_url}?path={path}', headers=self.headers)
        if response.status_code == 201:
            logging.info(f'Folder "{path}" created successfully.')
        elif response.status_code == 409:
            logging.info(f'Folder "{path}" already exists.')
        else:
            logging.error(f'Failed to create folder: {response.status_code}, {response.text}')
            response.raise_for_status()

    def upload_photos_to_yd(self, path, url_file, name):
        params = {"path": f'/{path}/{name}', "url": url_file, "overwrite": "true"}
        response = requests.post(self.upload_url, headers=self.headers, params=params)
        if response.status_code == 202:
            logging.info(f'File "{name}" uploaded successfully.')
        else:
            logging.error(f'Failed to upload file "{name}": {response.status_code}, {response.text}')
            response.raise_for_status()


def get_sub_breeds(breed):
    try:
        response = requests.get(f'https://dog.ceo/api/breed/{breed}/list', timeout=10)
        response.raise_for_status()
        return response.json().get('message', [])
    except requests.RequestException as e:
        logging.error(f'Failed to get sub-breeds for breed "{breed}": {e}')
        return []


def get_urls(breed, sub_breeds):
    url_images = []
    try:
        if sub_breeds:
            for sub_breed in sub_breeds:
                res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random", timeout=10)
                res.raise_for_status()
                sub_breed_url = res.json().get('message')
                url_images.append(sub_breed_url)
        else:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random", timeout=10)
            res.raise_for_status()
            url_images.append(res.json().get('message'))
    except requests.RequestException as e:
        logging.error(f'Failed to get images for breed "{breed}": {e}')
    return url_images


def upload_dog_images(breed, uploader, folder_name):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    uploader.create_folder(folder_name)

    for url in urls:
        if url:
            parsed_url = urlparse(url)
            part_name = os.path.basename(parsed_url.path)
            name = f"{breed}_{part_name}"
            uploader.upload_photos_to_yd(folder_name, url, name)


@pytest.mark.parametrize('breed', ['doberman', 'bulldog', 'labrador', 'poodle'])
def test_proverka_upload_dog(breed):
    token = os.getenv("YANDEX_DISK_TOKEN")
    if not token:
        raise EnvironmentError("Yandex Disk token not found. Please set the YANDEX_DISK_TOKEN environment variable.")
    uploader = YaUploader(token)
    folder_name = "test_folder"
    
    upload_dog_images(breed, uploader, folder_name)

    # Проверка, что папка была создана
    response = requests.get(f'{uploader.base_url}?path=/{folder_name}', headers=uploader.headers)
    response.raise_for_status()
    assert response.json().get('type') == "dir", f"Expected 'dir', got {response.json().get('type')}"
    assert response.json().get('name') == folder_name, f"Expected folder name '{folder_name}', got {response.json().get('name')}"

    # Проверка файлов в папке
    items = response.json().get('_embedded', {}).get('items', [])
    expected_count = len(get_sub_breeds(breed)) if get_sub_breeds(breed) else 1
    assert len(items) == expected_count, f"Expected {expected_count} files, but found {len(items)}"
    
    for item in items:
        assert item['type'] == 'file', f"Expected 'file', got {item['type']}"
        assert item['name'].startswith(breed), f"File name '{item['name']}' does not start with breed '{breed}'"
