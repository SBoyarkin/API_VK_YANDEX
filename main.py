from datetime import datetime
from tqdm import tqdm
import json
import requests
import configparser


class Application:
    def __init__(self, vk_user_id, vk_access_token, yandex_access_token, folder_name=datetime.now().date(), count=5,):
        self.yandex_access_token = yandex_access_token
        self.vk_user_id = vk_user_id
        self.vk_access_token = vk_access_token
        self.count = count
        self.api_server = 'api.vk.com/'
        self.params = {
            'access_token':  self.vk_access_token,
            'owner_id': self.vk_user_id,
            'album_id': 'profile',
            'extended': '1',
            'count': self.count,
            'v': '5.199',
        }
        self.yandex_api_server = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.folder_name = folder_name
        self.params_yandex = {
            'path': {self.folder_name}
        }
        self.headers_yandex = {
            'Authorization': f'OAuth {self.yandex_access_token}'
        }

    def get_photo(self):
        photo_list = {}
        response = requests.post('https://api.vk.com/method/photos.get', params=self.params)
        photos = response.json()['response']['items']
        for photo in tqdm(photos, postfix='Получение списка фото', colour='blue'):
            if photo['likes']['count'] in photo_list:
                photo_list[f"{photo['likes']['count']}_{datetime.fromtimestamp(photo['date']).date()}"] = photo['sizes'][5]
            else:
                photo_list[photo['likes']['count']] = photo['sizes'][5]
        self.__push_photo(photo_list)
        return photo_list

    def __push_photo(self, photo_lst):
        json_lst = []
        requests.put(f'{self.yandex_api_server}/', params=self.params_yandex, headers=self.headers_yandex)
        for key, value in tqdm(photo_lst.items(), colour='green', postfix=f'Загрузка фото на Яндекс Диск'):
            url = (value['url'])
            params = {'url': url, 'path': f"{self.folder_name}/{key}.jpg"}
            upload = requests.post(f'{self.yandex_api_server}/upload/', params=params, headers=self.headers_yandex)
            if upload.status_code == 202:
                json_lst.append({'file_name': f'{key}.jpg', 'size': value['type']})
        self.__push_json_file(json_lst)
        self.__check_download_file(json_lst, photo_lst)
        return

    def __push_json_file(self, js):
        js = json.dumps(js)
        params = {'path': f"{self.folder_name}/info.json", 'overwrite': 'true'}
        response = requests.get(f'{self.yandex_api_server}/upload/', params=params, headers=self.headers_yandex)
        push_file = requests.put(response.json()['href'], js)
        return push_file

    def __check_download_file(self, json_list, photo_list):
        if len(json_list) == len(photo_list):
            print('Все файлы успешно загружены')
        else:
            'Не все файлы были загружены'


config = configparser.ConfigParser()
config.read("conf.ini")


user_id = config['backup']['vk_user_id']
vk_token = config['backup']['vk_access_token']
yandex_token = config['backup']['yandex_access_token']

boyarkin = Application(vk_user_id=user_id, vk_access_token=vk_token,
                       yandex_access_token=yandex_token)
boyarkin.get_photo()
