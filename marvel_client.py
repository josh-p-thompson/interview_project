import time
import hashlib

import requests


class Marvel:
    def __init__(self, public_key, private_key):
        self._public_key = public_key
        self._private_key = private_key

    def all(self, offset=0):
        """ Calls /characters for all characters """
        return self._call_api(
            endpoint='characters',
            offset=offset,
            limit=100
        )

    def character(self, id, offset=0):
        """ Calls /characters/{character_id} for single character """
        return self._call_api(
            endpoint='characters/' + str(id),
            offset=offset,
            limit=100
        )

    def character_comics(self, id, offset=0):
        """ Calls /characters/{character_id}/comics for character's comics """
        return self._call_api(
            endpoint='characters/' + str(id) + '/comics',
            offset=offset,
            limit=100
        )

    def _call_api(self, endpoint, **kwargs):
        """ Handles all API calls """
        kwargs['ts'] = str(int(time.time()*1000))
        kwargs['hash'] = self._generate_hash(kwargs['ts'])
        kwargs['apikey'] = self._public_key
        response = requests.get(
            'https://gateway.marvel.com/v1/public/' + endpoint,
            params=kwargs,
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error Code: {response.status_code}')
            print(response.json())
            raise ValueError(
                f"""
                Error Code: {response.status_code}.
                Response: {response.json()}
                """
            )

    def _generate_hash(self, ts):
        """ Generates required hash for all API calls """
        combined = ts + self._private_key + self._public_key
        combined = combined.encode()
        return hashlib.md5(combined).hexdigest()
