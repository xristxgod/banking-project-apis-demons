from __future__ import absolute_import

import logging

from ._load_env import env_vault

__all__ = (
    'settings',
)

BASE_SETTINGS_STRUCTURE_FIELDS = [
    'ROOT_DIR', 'CONFIG_DIR', 'CONTRACTS_DIR',
    'CONTRACTS_FILE',
]


class SettingsMeta(type):
    base_dir_name = 'settings'

    load_from_module_names = (
        'common', 'dev',
    )

    def __new__(mcs, name: str, basses: tuple, attribute: dict):
        # # Load from env :: Vault service
        for key, value in env_vault.env.items():
            setattr(mcs, key, value)

        moduls = mcs.load_from_module_names
        if attribute.get('from_dir'):
            moduls = attribute['from_dir']

        settings_structure = BASE_SETTINGS_STRUCTURE_FIELDS
        if attribute.get('settings_structure'):
            settings_structure = attribute['settings_structure']

        for module_name in moduls:
            module_path = f'{mcs.base_dir_name}.{module_name}'

            try:
                module = __import__(module_path, globals(), locals(), settings_structure, 0)
            except ModuleNotFoundError:
                logging.warning(f'Module: {module_path} not found')
                continue

            for attr in module.__dict__:
                if attr in settings_structure:
                    attribute.update({attr: getattr(module, attr)})

        return super(SettingsMeta, mcs).__new__(mcs, name, basses, attribute)


class Settings(metaclass=SettingsMeta):
    from_dir: tuple | list = None
    settings_structure: tuple | list = None

    class SettingsNotFound(Exception):
        pass


class TestSettings(Settings):
    from_dir = ('test',)


settings = Settings()
