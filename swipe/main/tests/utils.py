from firebase_admin import auth as firebase_auth

from swipe.config import WEB_API_KEY

import requests
from PIL import Image


_TEST_USER_EMAIL = 'user@example.com'
_TEST_UID = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
_ENDPOINT = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}'


def get_id_token(test_uid=_TEST_UID):
    user = firebase_auth.get_user(test_uid)
    custom_token = firebase_auth.create_custom_token(user.uid)
    url = _ENDPOINT.format(api_key=WEB_API_KEY)
    data = {
        'token': custom_token,
        'returnSecureToken': True
    }
    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json()['idToken']


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new('RGBA', size, color)
    image.save(temp_file, 'png')
    return temp_file
