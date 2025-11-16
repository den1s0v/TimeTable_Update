import logging
import time
from fs.googledrivefs import GoogleDriveFS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.api_core.exceptions import RetryError
from timetable.models import Storage
from .storage_manager import StorageManager


class StorageManagerGoogleDrive(StorageManager):
    def __init__(self, storage_type: str, json_file_path: str):
        """
        Создаёт объект
        :param storage_type:
        :param json_file_path:
        """
        # Инициализация подключеничения
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_file(
            json_file_path, scopes=SCOPES
        )

        # Подключение в библиотеке GoogleDriveFS
        fs = GoogleDriveFS(creds)
        # Подключение напрямую для получения id файлов
        self._service = build("drive", "v3", credentials=creds)
        # Инициализация родительского класса
        super().__init__(storage_type, fs)

    def _set_storage_link(self, file_dir: str, storage: Storage):
        # Определить ID файла
        file_id = self.__get_file_id(file_dir)
        dir_id = self.__get_dir_id(file_dir)

        # Сохранить ссылки для скачивания и просмотра в записи базы данных
        storage.download_url = self.__get_download_url(file_id)
        storage.resource_url = self.__get_view_url(file_id)
        storage.archive_url = self.__get_dir_view_url(dir_id)

        # Вернуть запись базы данных со ссылками
        return storage

    def _make_file_public(self, file_dir: str):
        # Получить ID файла
        file_id = self.__get_file_id(file_dir)

        # Определить набор прав доступа
        permission = {
            "type": "anyone",  # доступ для всех
            "role": "reader",  # доступ только для чтения
        }

        # Применяем новые права доступа к файлу
        self._service.permissions().create(fileId=file_id, body=permission).execute()

    def _make_dir_public(self, file_dir: str):
        # Получаем ID папки
        folder_id = self.__get_dir_id(file_dir)

        # Настраиваем права доступа для папки
        permission = {
            "type": "anyone",  # доступ для всех
            "role": "reader",  # доступ только для чтения
        }
        self._service.permissions().create(fileId=folder_id, body=permission).execute()

    def __get_file_id(self, path):
        """
        Опредляет id файла или директории.
        :param path: Путь.
        :return: ID.
        """
        # Вернуть id файла или директории
        return self._fs_root.getinfo(path).raw["sharing"]["id"]

    def __get_dir_id(self, path):
        """
        Получает ID родительской папки.
        :param path: Путь к файлу или директории.
        :return: ID родительской папки.
        """
        # Получаем ID файла или директории из пути
        file_id = self.__get_file_id(path)

        # Запрашиваем метаданные файла через Google Drive API
        file_metadata = (
            self._service.files().get(fileId=file_id, fields="parents").execute()
        )

        # Извлекаем родительский ID
        parents = file_metadata.get("parents")
        if not parents:
            raise ValueError(
                "Указанный файл или директория не имеют родительской папки."
            )
        return parents[0]  # Google Drive всегда возвращает список родителей

    @staticmethod
    def __get_download_url(file_id):
        """
        Возвращает ссылку на скачивание файла.
        :param file_id: ID файла.
        :return: Ссылка на скачивание
        """
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    @staticmethod
    def __get_view_url(file_id):
        """
        Возвращает ссылку на просмотр файла.
        :param file_id: ID файла.
        :return: Ссылка на просмотр файла.
        """
        return f"https://drive.google.com/file/d/{file_id}/view"

    @staticmethod
    def __get_dir_view_url(dir_id: str) -> str:
        """
        Возвращает ссылку на просмотр папки.
        :param dir_id: ID файла.
        :return: Ссылка на просмотр директории.
        """
        # Возвращаем ссылку на просмотр
        return f"https://drive.google.com/drive/folders/{dir_id}"
