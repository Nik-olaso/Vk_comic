import requests
import os
from dotenv import load_dotenv
import random


def download_random_comic():
    comic_url = "https://xkcd.com/info.0.json"
    response = requests.get(comic_url)
    response.raise_for_status()
    response = response.json()
    comic_number = response['num']
    random_comic_url = f"https://xkcd.com/{random.randint(0, comic_number)}/info.0.json"
    comic_response = requests.get(random_comic_url)
    comic_response.raise_for_status()
    comic_response = comic_response.json()
    filename = f'{comic_response["title"]}.png'
    comic_link = comic_response["img"]
    author_comment = comic_response["alt"]
    comic_response = requests.get(comic_link)
    comic_response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(comic_response.content)
    return filename, author_comment


def get_wall_upload_server(access_token, group_id, api_version):
    upload_params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': api_version
    }
    vk_upload_response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=upload_params)
    vk_upload_response.raise_for_status()
    vk_upload_response = vk_upload_response.json() 	
    if 'error' in vk_upload_response:
        raise requests.exceptions.HTTPError(vk_upload_response['error']['error_msg'])
    upload_url = vk_upload_response['response']['upload_url']
    return upload_url


def get_photo_params(filename, upload_url):
    with open(filename, 'rb') as open_file:
        file = {'file1': open_file}
        upload_response = requests.post(upload_url, files=file)
    upload_response.raise_for_status()
    upload_response = upload_response.json() 
    return upload_response['photo'], upload_response['server'], upload_response['hash']


def save_wall_photo(access_token, group_id, api_version, upload_photo, upload_server, upload_hash):
    save_params = {
        'access_token':access_token,
        'group_id': group_id,
        'photo': upload_photo,
        'server': upload_server,
        'hash': upload_hash,
        'v': api_version
    }
    vk_save_response = requests.get('https://api.vk.com/method/photos.saveWallPhoto', params=save_params)
    vk_save_response.raise_for_status()
    vk_save_response = vk_save_response.json() 	
    if 'error' in vk_save_response:
        raise requests.exceptions.HTTPError(vk_save_response['error']['error_msg'])
    owner_id = vk_save_response['response'][0]['owner_id']
    media_id = vk_save_response['response'][0]['id']
    attachments = f'photo{owner_id}_{media_id}'
    return attachments


def post_wall_photo(access_token, group_id, api_version, attachments, author_comment):
    post_params = {
        'attachments': attachments,
        'message' : author_comment,
        'owner_id': f'-{group_id}',
        'access_token': access_token,
        'from_group': '1',
        'v': api_version
    }
    photo_response = requests.post('https://api.vk.com/method/wall.post', params=post_params)
    photo_response.raise_for_status()
    photo_response = photo_response.json() 	
    if 'error' in photo_response:
        raise requests.exceptions.HTTPError(photo_response['error']['error_msg'])    
    

def main():
    load_dotenv()
    group_id = os.environ["VK_GROUP_ID"]
    access_token = os.environ["VK_ACCESS_TOKEN"]
    api_version = "5.131"
    filename, author_comment = download_random_comic()
    upload_url = get_wall_upload_server(access_token, group_id, api_version)
    try:
        upload_photo, upload_server, upload_hash = get_photo_params(filename, upload_url)
        attachments = save_wall_photo(access_token, group_id, api_version, upload_photo, upload_server, upload_hash)
        post_wall_photo(access_token, group_id, api_version, attachments, author_comment)
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()
