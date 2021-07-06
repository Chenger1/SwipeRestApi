from firebase_admin import auth as firebase_auth

from swipe.config import WEB_API_KEY

import requests


_TEST_USER_EMAIL = 'user@example.com'
_TEST_UID = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
_ENDPOINT = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}'


def get_id_token():
    user = firebase_auth.get_user(_TEST_UID)
    custom_token = firebase_auth.create_custom_token(user.uid)
    url = _ENDPOINT.format(api_key=WEB_API_KEY)
    data = {
        'token': custom_token,
        'returnSecureToken': True
    }
    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json()['idToken']
