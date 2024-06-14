from PySide6.QtWidgets import QFileDialog
from datetime import datetime, timedelta
from typing import Dict
import json


# Базовый класс.
class DataFile:

    # Выбор файла с помощью диалогового окна и возврат пути к выбранному файлу.
    # noinspection PyMethodMayBeStatic
    def get_file_path(self, type_file: str) -> str | None:
        file_dialog = QFileDialog()  # Создание объекта диалогового окна.
        file_dialog.setNameFilter(
            f'Text files (*.{type_file})')  # Фильтр для отображения только файлов переданного типа.
        if file_dialog.exec():  # Проверка того, что пользователь выбрал файл.
            return file_dialog.selectedFiles()[0]  # Возврат пути к выбранному файлу.
        return None

    # Чтение данных из файла.
    # noinspection PyMethodMayBeStatic
    def read_file(self, file_path: str, type_file: str) -> list | dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                return file.readlines() if type_file == 'txt' else json.load(file)
        except Exception as e:
            print(f'Error reading file: {e}')
            return None

    # Открытие и считывание текстового файла.
    def open_file(self, type_file: str) -> None:
        get_file_path_method = getattr(self, f'get_file_path_{type_file}')
        read_file_method = getattr(self, f'read_file_{type_file}')
        process_data_method = getattr(self, f'process_data_{type_file}')

        file_path: str = get_file_path_method()  # Получение пути к файлу.
        if file_path:  # Проверка условия того, что файл выбран.
            lines: list | dict = read_file_method(file_path)  # Считывание содержимого файла в переменную "lines"
            if lines:  # Содержимое файла не пустое.
                process_data_method(lines)  # Обработка содержимого файла.


# Класс обработки файла типа ".txt"
class DataText(DataFile):

    def __init__(self):
        self.txt_data = {}  # Словарь результатов.

    def open_txt_file(self) -> None:
        super().open_file(type_file='txt')

    def get_file_path_txt(self) -> str:
        return super().get_file_path(type_file='txt')

    def read_file_txt(self, file_path: str) -> list | None:
        return super().read_file(file_path, type_file='txt')

    def process_data_txt(self, lines: list) -> None:
        for line in lines:
            parts = line.split()
            key: str = parts[0].strip('\ufeff')  # Идентификатор спортсмена.
            time_str: str = parts[2]
            self.update_data(key, time_str)
        self.sort_data()
        self.format_time()

    # Формирование словаря с результатами рейтингов.
    def update_data(self, key: str, time_str: str) -> None:
        time_obj = datetime.strptime(time_str, '%H:%M:%S,%f')
        if key not in self.txt_data:
            self.txt_data[key]: Dict[str, datetime] = {'start': time_obj}
        else:
            start_time: datetime = self.txt_data[key].pop('start')
            self.txt_data[key]['result']: timedelta = time_obj - start_time

    # Сортировка словаря с результатами рейтингов.
    def sort_data(self) -> None:
        self.txt_data = dict(sorted(self.txt_data.items(), key=lambda x: x[1].get('result', datetime.min)))

    # Приведение результатов рейтингов к необходимому формату времени.
    def format_time(self) -> None:
        def format_timedelta(td: timedelta) -> str:
            minutes, seconds = divmod(td.seconds, 60)
            return f"{minutes:02}:{seconds:02},{td.microseconds // 10000:02}"

        self.txt_data = dict(
            map(lambda x: (x[0], {'result': format_timedelta(x[1]['result'])}), list(self.txt_data.items())))


# Класс обработки файла типа ".json"
class DataJson(DataFile):
    def __init__(self):
        self.json_data = {}

    def open_json_file(self) -> None:
        super().open_file(type_file='json')

    def get_file_path_json(self):
        return super().get_file_path(type_file='json')

    def read_file_json(self, file_path: str) -> list | None:
        return super().read_file(file_path, type_file='json')

    def process_data_json(self, lines: dict) -> None:
        self.json_data = {i[0].strip('\ufeff'): i[1] for i in lines.items()}
