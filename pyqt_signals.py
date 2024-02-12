__author__ = "Pavel M Kozlovski"
__email__  = "zork03@yandex.ru"
__date__   = "12.02.2024"

"""
Тестовое задание.

Разработать оконную программу (используя PyQT).

Разработать программу, которая
в одном потоке наполняет очередь сообщений json-пакетами,
вида {"имя_параметра" : значение},
а в другом разбирает эту очередь
и заполняет предоставленную форму.

testform.ui - форма, которую нужно заполнить.

В tableView должна отобразиться таблица
- в первом столбце имена параметров,
во втором текущее значение.

Также значение пришедшего параметра должно попасть
в соответствующий lineEdit.

Возможные имена параметров
- "Signal 1", "Signal 2", "Signal 3".
Значения - рандомные числа.

Покройте свою программу тестами.

В качестве результата ожидаю
архив репозитория, в котором делалось тестовое задание,
со всеми необходимыми для запуска программы файлами.
"""

import json
import queue
import random
import sys

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtCore import Qt


class SenderThread(QtCore.QThread):
    """
    Класс потока отправителя сообщений
    """

    def __init__(self, messageQueue, sendTimeout):
        """
        Инициализация потока отправителя сообщений

        :param messageQueue: Очередь сообщений
        :param sendTimeout: Временная задержка между отправкой сообщений (в миллисекундах)
        """
        super(SenderThread, self).__init__()

        self.messageQueue = messageQueue
        self.sendTimeout = sendTimeout

    @staticmethod
    def generateRandomParam():
        """
        Сгенерировать параметр с случайным значением

        :return: Пара значений ("Имя параметра", Значение параметра)
        """
        paramName = random.choice(("Signal 1", "Signal 2", "Signal 3"))
        paramValue = random.randrange(0, 100)

        return paramName, paramValue

    def run(self):
        """
        Отправка сообщений
        """
        while True:

            # сгенерировать параметр с случайным значением
            paramName, paramValue = self.generateRandomParam()

            print(f'Send Param: name="{paramName}", value={paramValue}')

            # создать json-сообщение
            message = json.dumps( {paramName: paramValue} )

            # поместить json-сообщение в очередь сообщений
            self.messageQueue.put(message)

            # временная задержка между отправкой сообщений
            self.msleep(self.sendTimeout)


class ReceiverThread(QtCore.QThread):
    """
    Класс потока получателя сообщений
    """

    # сигнал о получении параметра
    incomingParam = QtCore.pyqtSignal(str, int)

    def __init__(self, messageQueue):
        """
        Инициализация потока получателя сообщений

        :param messageQueue: Очередь сообщений
        """
        super(ReceiverThread, self).__init__()

        self.messageQueue = messageQueue

    def run(self):
        """
        Получение сообщений
        """
        while True:

            # получить json-сообщение из очереди
            message = self.messageQueue.get()

            # извлечь имя и значение параметра из json-сообщения
            paramName, paramValue = json.loads(message).popitem()

            print(f'Receive Param: name="{paramName}", value={paramValue}')

            # отправить сигнал о получении параметра
            self.incomingParam.emit(paramName, paramValue)


class ParamTable(QtCore.QAbstractTableModel):
    """
    Класс таблицы параметров (модель)
    """

    def __init__(self):
        """
        Инициализация таблицы параметров
        """
        super(ParamTable, self).__init__()

        # заголовки столбцов таблицы
        self.tableHeader = ["Параметр", "Значение"]

        # данные ячеек таблицы
        self.tableData = [
            ["Signal 1", ""],
            ["Signal 2", ""],
            ["Signal 3", ""],
        ]

    def rowCount(self, index):
        """
        Получить количество строк в таблице
        """
        return len(self.tableData)

    def columnCount(self, index):
        """
        Получить количество столбцов в таблице
        """
        return len(self.tableData[0])

    def headerData(self, section, orientation, role):
        """
        Получить значение заголовка столбца
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.tableHeader[section]

    def data(self, index, role):
        """
        Получить значение ячейки таблицы
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return self.tableData[index.row()][index.column()]

    def setParamValue(self, row, value):
        """
        Установить значение параметра в соответствующую строку таблицы

        :param row: Номер строки таблицы
        :param value: Значение параметра
        """
        index = self.index(row, 1)
        if index.isValid():
            self.tableData[row][1] = str(value)
            self.dataChanged.emit(index, index)


class TestForm(QtWidgets.QWidget):
    """
    Класс тестовой формы
    """

    def __init__(self):
        """
        Инициализация тестовой формы
        """
        super(TestForm, self).__init__()

        # загрузить тестовую форму из файла
        uic.loadUi("testform.ui", self)

        # создать таблицу параметров
        self.paramTable = ParamTable()
        self.tableView.setModel(self.paramTable)

    def setParam(self, paramName, paramValue):
        """
        Установить значение параметра в поля тестовой формы

        :param paramName: Имя параметра
        :param paramValue: Значение параметра
        """
        strParamValue = str(paramValue)

        if paramName == "Signal 1":
            self.paramTable.setParamValue(0, paramValue)
            self.lineEdit.setText(strParamValue)

        elif paramName == "Signal 2":
            self.paramTable.setParamValue(1, paramValue)
            self.lineEdit_2.setText(strParamValue)

        elif paramName == "Signal 3":
            self.paramTable.setParamValue(2, paramValue)
            self.lineEdit_3.setText(strParamValue)


class MainWindow(QtWidgets.QMainWindow):
    """
    Класс главного окна
    """

    def __init__(self):
        """
        Инициализация главного окна
        """
        super(MainWindow, self).__init__()

        self.setWindowTitle("PyQt Signals")

        # создать тестовую форму
        self.testForm = TestForm()
        self.setCentralWidget(self.testForm)


class Application(QtWidgets.QApplication):
    """
    Класс приложения
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализация приложения
        """
        super(Application, self).__init__(*args, **kwargs)

        # создать главное окно
        self.mainWindow = MainWindow()
        self.mainWindow.show()

        # создать очередь сообщений для передачи json-сообщений между потоками
        self.messageQueue = queue.Queue()

        # создать поток получатель сообщений
        self.receiverThread = ReceiverThread(self.messageQueue)
        # подключить сигнал о получении параметра к методу установки значения параметра в тестовой форме
        self.receiverThread.incomingParam.connect(self.mainWindow.testForm.setParam)
        self.receiverThread.start()

        # создать поток отправитель сообщений
        # временная задержка между отправкой сообщений 1 секунда
        self.senderThread = SenderThread(self.messageQueue, sendTimeout=1000)
        self.senderThread.start()

        ## потоки автоматически останавливаются при завершении программы


def main():
    """
    Запуск программы
    """
    app = Application(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

