import random
import pytest
import requests


class YaUploader:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, path):
        response = requests.put(f'{self.base_url}?path={path}', headers=self.headers)
        if response.status_code != 201 and response.status_code != 409:
            raise Exception(f'Failed to create folder: {response.status_code}, {response.text}')

    def upload_photos_to_yd(self, path, url_file, name):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        response = requests.post(upload_url, headers=self.headers, params=params)
        if response.status_code != 202:
            raise Exception(f'Failed to upload file: {response.status_code}, {response.text}')


def get_sub_breeds(breed):
    response = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
    if response.status_code != 200:
        raise Exception(f'Failed to get sub-breeds: {response.status_code}, {response.text}')
    return response.json().get('message', [])


def get_urls(breed, sub_breeds):
    url_images = []
    try:
        if sub_breeds:
            for sub_breed in sub_breeds:
                res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
                if res.status_code == 200:
                    sub_breed_urls = res.json().get('message')
                    url_images.append(sub_breed_urls)
                else:
                    raise Exception(f'Failed to get image for sub-breed {sub_breed}: {res.status_code}, {res.text}')
        else:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
            if res.status_code == 200:
                url_images.append(res.json().get('message'))
            else:
                raise Exception(f'Failed to get image for breed {breed}: {res.status_code}, {res.text}')
    except Exception as e:
        print(e)
    return url_images


def upload_dog_images(breed, uploader, folder_name):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    uploader.create_folder(folder_name)
    
    for url in urls:
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        uploader.upload_photos_to_yd(folder_name, url, name)


@pytest.mark.parametrize('breed', ['doberman', 'bulldog'])
def test_proverka_upload_dog(breed):
    token = "AgAAAAAJtest_tokenxkUEdew"
    uploader = YaUploader(token)
    folder_name = "test_folder"
    upload_dog_images(breed, uploader, folder_name)
    
    # Проверка, что папка была создана
    response = requests.get(f'{uploader.base_url}?path=/{folder_name}', headers=uploader.headers)
    assert response.status_code == 200, f"Folder not found: {response.status_code}, {response.text}"
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == folder_name
    
    # Проверка файлов в папке
    items = response.json().get('_embedded', {}).get('items', [])
    expected_count = len(get_sub_breeds(breed)) if get_sub_breeds(breed) else 1
    assert len(items) == expected_count, f"Expected {expected_count} files, but found {len(items)}"
    
    for item in items:
        assert item['type'] == 'file'
        assert item['name'].startswith(breed)
