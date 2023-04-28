import os
import abc
import time
from typing import Type

import requests


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def get_envs(self) -> dict: ...


class VaultStorage(BaseStorage):
    url = os.getenv('VAULT_URL', '')
    storage_paths = tuple(os.getenv('VAULT_STORAGE_PATHS', []))

    auth_data = {
        'role_id': os.getenv('VAULT_ROLE_ID'),
        'secret_id': os.getenv('VAULT_SECRET_ID')
    }

    def __init__(self):
        self._auth_token = None
        self._storage_url = os.path.join(self.url, '/v1/secrets/data')

    @property
    def headers(self) -> dict:
        return {
            'X-Vault-Token': self._auth_token
        }

    def auth(self):
        response = requests.request(
            'POST',
            url=os.path.join(self.url, '/v1/auth/approle/login'),
            data=self.auth_data,
        ).json()
        self._auth_token = response['auth']['client_token']

    def get_envs(self) -> dict:
        self.auth()

        envs = {}
        for path in self.storage_paths:
            response = requests.request(
                'GET',
                url=os.path.join(self._storage_url, path),
                headers=self.headers
            ).json()
            envs.update(response['data']['data'])
        return envs


class LoadSettings:
    def __init__(self, storage_cls: Type[BaseStorage]):
        self._storage = storage_cls()

        self._raw_env = None
        self._settings_obj = None

        self.last_update_time = None

        self.update()

    def update(self):
        self._raw_env = self._storage.get_envs()
        self._create_obj()
        self.last_update_time = int(time.time())

    def _create_obj(self):
        self._settings_obj = type('Env', (), {})
        for key, value in self._raw_env.items():
            setattr(self._settings_obj, key.upper(), value)

        def settings_getattr(obj, item):
            try:
                return object.__getattribute__(obj, item)
            except AttributeError:
                raise AttributeError(f'Env: {item} not found')

        self._settings_obj.__getattribute__ = settings_getattr

    @property
    def obj(self) -> dict:
        if not self._settings_obj:
            self._create_obj()
        return self._settings_obj


load_settings = LoadSettings(storage_cls=VaultStorage)
