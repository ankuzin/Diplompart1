import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG, filename="Сохранение логов программы.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

token_ya = 'AQAAAAAbNlnQAADLW8LZQTcZtEzAhR'
token_vk = '73e963cb7bfaeb30183ab67cf63e81'
id_vk = '23408234'

class YaUploader:
    def __init__(self, token_ya, token_vk):
        self.token_ya = token_ya
        self.token_vk = token_vk
        self.temporary_url = []
        self.temporary_sizes = []
        self.list_url = []
        self.list_sizes = []
        self.list_likes = []
        self.list_upload_date = []
        self.list_load_foto = []
        self.json_file_info = []
        self.name_folder = ''

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def creature_folder_ya(self, name_folder):  # создание папки на ya.диске для фотографий с vk
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {'path': name_folder}
        response = requests.put(url=url, headers=headers, params=params)
        self.name_folder += name_folder
        if response.status_code == 201:
            print(f'Папка {name_folder} успешно добавлена на ЯНДЕКС диск')
        else:
            print(f'К сожалению папка {name_folder} уже есть на ЯНДЕКС диске \n'
                  f'Попробуйте добавить папку с другим именем')

    def receiving_foto_vk(self, owner_id_vk):  # получение и сохранение фотографий с vk на яндекс.диск
        url = 'http://api.vk.com/method/photos.get'
        params = {'album_id': 'profile', 'extended': '1', 'photo_sizes': '1',
        'owner_id': owner_id_vk , 'access_token': self.token_vk, 'v': '5.131'}
        response = requests.get(url=url, params=params)
        link_load = response.json()

        for link in link_load['response']['items']:  # создание списка количества лайков
            for like in link['likes'].values():
                if like > 1:
                    self.list_likes.append(f' {like}.jpg')
        for date in link_load['response']['items']:  # создание списка  даты загрузки
            self.list_upload_date.append(date['date'])
        dict_dl_ll = dict(zip(self.list_upload_date, self.list_likes))

        for link in link_load['response']['items']:  # создание списков  форматов фото и url
            max_dpi = 0
            element_url = 'none'
            element_type = 'none'
            for sizes in link['sizes']:
                if sizes['height'] > 0 and sizes['height'] > 0:
                    dpi = sizes['height'] * sizes['height']
                    if dpi > max_dpi:
                        max_dpi = dpi
                        element_url = sizes['url']
                        element_type = sizes['type']
                elif sizes['type'] == 'y':
                    self.temporary_url.append(sizes['url'])
                    self.temporary_sizes.append(sizes['type'])
            self.temporary_url.append(element_url)
            self.temporary_sizes.append(element_type)
        for url in self.temporary_url:
            if url != 'none':
                self.list_url.append(url)
        for size in self.temporary_sizes:
            if size != 'none':
                self.list_sizes.append(size)

        for date, name in dict_dl_ll.items():  # создание имен фотографий для загрузки
            if name not in self.list_load_foto:
                self.list_load_foto.append(name)
            else:
                self.list_load_foto.append(date)
        dict_u_ll = dict(zip(self.list_url, self.list_load_foto))

        for url_d, name in dict_u_ll.items():  # загрузка фотографий в ya.диск
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload/"
            headers = self.get_headers()
            params = {'path': f'disk:/{self.name_folder}/{name}', 'url': url_d}
            response = requests.post(url=url, headers=headers, params=params)
        if response.status_code == 202:
            print('Фотографии успешно загружены')
        else:
            print('К сожалению неудалось загрузить фотографии')

        dict_lz = dict(zip(self.list_load_foto, self.list_sizes))  # создание json-файла с информацией по файлу загрузки
        for name, size in dict_lz.items():
            self.json_file_info.append({
                'file_name': f'{name}',
                'size': f'{size}',
                'path': f'disk:/{self.name_folder}/{name}'
            })
            with open('json файл с информацией по фотографиям .txt', 'w') as outfile:
                json.dump(self.json_file_info, outfile)


if __name__ == '__main__':
    ya = YaUploader(token_ya=token_ya, token_vk=token_vk)
    ya.creature_folder_ya('VK')
    ya.receiving_foto_vk(owner_id_vk=id_vk)
