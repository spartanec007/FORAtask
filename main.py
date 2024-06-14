from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from data_processor import DataText, DataJson
import json
import sys

buttons = [
    {'name': 'Добавить личные данные спортсменов\n(.json)', 'action': 'open_json_file'},
    {'name': 'Добавить результаты спортсменов\n(.txt)', 'action': 'open_txt_file'},
    {'name': 'Расчет рейтингов', 'action': 'calculation_results'},
    {'name': 'Сохранить результат расчета рейтингов', 'action': 'save_result'},
]


# Приложение.
class CenteredWidget(QWidget, DataText, DataJson):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Калькулятор расчета рейтингов спортсменов')
        self.table_widget = None
        self.setup_layout()
        self.setFixedSize(774, 422)
        self.union_data = {}  # Словарь после объединения данных файлов ".txt" и ".json"
        self.formatted_data = {}  # Итоговый словарь с данными после их обработки.

    # Инициализация макета для виджетов.
    def setup_layout(self) -> None:
        layout = QVBoxLayout()  # Вертикальный блок из себя представляет контейнер в который мы помещаем элементы.
        self.setLayout(layout)  # Установка вертикального блока в качестве компоновщика главного окна
        for btn in buttons:  # Добавление кнопок.
            self.button(layout, btn)
        self.table(layout)  # Добавление таблицы.

    # Создание таблицы.
    def table(self, layout: QVBoxLayout) -> None:
        self.table_widget = QTableWidget()  # Создание объекта таблицы.
        self.table_widget.setColumnCount(5)  # Устанавливаем количество столбцов
        self.table_widget.setRowCount(5)  # Устанавливаем количество строк
        self.table_widget.setHorizontalHeaderLabels(
            ['Занятое место', 'Нагрудный номер', 'Имя', 'Фамилия', 'Результат'])  # Установка заголовков таблицы.
        self.table_widget.verticalHeader().setVisible(False)  # Скрыть нумерацию строк.
        self.table_widget.horizontalHeader().setMinimumSectionSize(150)  # Установка минимальной ширины столбца.
        layout.addWidget(self.table_widget)  # Добавление таблицы в главное окно приложения.

    # Создание кнопки.
    def button(self, layout: QVBoxLayout, context: dict) -> None:
        button = QPushButton(context["name"])  # Надпись кнопки.
        try:
            button.setMinimumSize(50, 50)  # Минимальные размеры кнопки.
            button.setStyleSheet("QPushButton:pressed { background-color: green; }")  # Анимация при нажатии на кнопку.
            button.clicked.connect(lambda: self.handle_button_click(context['action']))  # Клик по кнопке.
        except KeyError:
            pass
        layout.addWidget(button)  # Добавление кнопки в главное окно приложения.

    # Создание связей между кнопками и функциями действий.
    def handle_button_click(self, action: str) -> None:
        if action == 'open_json_file':
            self.open_json_file()
        elif action == 'open_txt_file':
            self.open_txt_file()
        elif action == 'calculation_results':
            self.calculation_results()
        elif action == 'save_result':
            self.save_result()

    # Расчет рейтингов.
    def calculation_results(self) -> None:
        self.union_data.update(self.txt_data)
        for key in self.union_data.keys():
            try:
                self.union_data[key].update(self.json_data[key])
            except Exception as e:
                print(e)
        self.format_data()
        self.add_data_table()

    # Получение итогового словаря с требуемыми заголовками данных.
    def format_data(self) -> None:
        for i, key in enumerate(self.union_data.keys()):
            self.formatted_data[f'{i + 1}'] = {'Нагрудный номер': key,
                                               'Имя': self.union_data[key]['Surname'],
                                               'Фамилия': self.union_data[key]['Name'],
                                               'Результат': self.union_data[key]['result']}

    # Добавление результатов (первые четыре места рейтинга) в таблицу приложения.
    def add_data_table(self) -> None:
        for i in range(1, 5):
            data: dict = self.formatted_data[str(i)]
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(i)))
            for j, key in enumerate(['Нагрудный номер', 'Имя', 'Фамилия', 'Результат']):
                self.table_widget.setItem(i, j + 1, QTableWidgetItem(data.get(key, '')))

    # Сохранение результатов в файл "result.json".
    def save_result(self) -> None:
        with open('result.json', 'w', encoding='utf-8') as file:
            json.dump(self.formatted_data, file, ensure_ascii=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    centered_widget = CenteredWidget()
    centered_widget.show()  # Отображение главного окна
    sys.exit(app.exec())  # Запуск главного цикла обработки событий приложения.
