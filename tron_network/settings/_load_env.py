import os
import abc
import time
from typing import Type

import requests


class BaseLoadFrom(abc.ABC):
    @abc.abstractmethod
    def get_envs(self) -> dict: ...


class LoadFromVault(BaseLoadFrom):
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


class EnvVault:
    def __init__(self, load_cls: Type[BaseLoadFrom]):
        self._storage = load_cls()
        self.env = self._storage.get_envs()


env_vault = EnvVault(load_cls=LoadFromVault)
