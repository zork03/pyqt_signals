__author__ = "Pavel M Kozlovski"
__email__  = "zork03@yandex.ru"
__date__   = "12.02.2024"

"""
Тесты для pyqt_signals
"""

import json
import queue
import random
import sys
import time
import unittest

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

import pyqt_signals


app = QApplication(sys.argv)


class ThreadsTest(unittest.TestCase):
    """
    Тесты потоков
    """

    def test_SenderThread(self):
        """
        Тест потока отправителя сообщений

        Поток запускается на 1 секунду.
        Сообщения из очереди сообщений проверяются на корректные значения.
        """
        messageQueue = queue.Queue()

        senderThread = pyqt_signals.SenderThread(messageQueue, sendTimeout=10)
        senderThread.start()

        time.sleep(1)

        senderThread.terminate()

        for message in messageQueue.queue:
            paramName, paramValue = json.loads(message).popitem()

            self.assertTrue( paramName in ("Signal 1", "Signal 2", "Signal 3") )
            self.assertTrue( int(paramValue) in range(100) )


    def test_ReceiverThread(self):
        """
        Тест потока получателя сообщений

        Создаётся тестовый список случайных параметров.
        Параметры из тестового списка помещаются в очередь сообщений потока.
        Поток запускается на 1 секунду, формируется список из пришедших параметров.
        Список пришедших параметров сравнивается с исходным списком параметров.
        """
        testParams = [
            [
                random.choice(("Signal 1", "Signal 2", "Signal 3")),
                random.randrange(0, 100)
            ]
            for i in range(100)
        ]

        messageQueue = queue.Queue()

        for paramName, paramValue in testParams:
            message = json.dumps( {paramName: paramValue} )
            messageQueue.put(message)

        incomingParams = []

        def paramCollector(paramName, paramValue):
            incomingParams.append( [paramName, paramValue] )

        receiverThread = pyqt_signals.ReceiverThread(messageQueue)
        receiverThread.incomingParam.connect( paramCollector )
        receiverThread.start()

        time.sleep(1)

        receiverThread.terminate()

        app.processEvents()

        # сравнить список пришедших параметров с исходным списком параметров
        self.assertEqual( incomingParams, testParams )


class TestFormTest(unittest.TestCase):
    """
    Тесты тестовой формы
    """

    def setUp(self):
        self.testForm = None


    def getRowCount(self):
        """
        Получить количество строк таблицы параметров
        """
        pt = self.testForm.paramTable
        return pt.rowCount( pt.index(0, 0) )

    def getColumnCount(self):
        """
        Получить количество столбцов таблицы параметров
        """
        pt = self.testForm.paramTable
        return pt.columnCount( pt.index(0, 0) )

    def getTableHeader(self):
        """
        Получить список заголовков столбцов таблицы параметров
        """
        pt = self.testForm.paramTable
        return [
            pt.headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            for section in range( self.getColumnCount() )
        ]

    def getTableData(self):
        """
        Получить данные таблицы параметров
        """
        pt = self.testForm.paramTable
        return [
            [
                pt.data( pt.index(row, column), Qt.ItemDataRole.DisplayRole )
                for column in range( self.getColumnCount() )
            ]
            for row in range( self.getRowCount() )
        ]

    def getLabelsLines(self):
        """
        Получить список пар значений виджетов Label и LineEdit тестовой формы
        """
        tf = self.testForm
        labelsLines = [
            [ tf.label,   tf.lineEdit   ],
            [ tf.label_2, tf.lineEdit_2 ],
            [ tf.label_3, tf.lineEdit_3 ],
        ]
        return [
            [
                widget.text()
                for widget in labelLine
            ]
            for labelLine in labelsLines
        ]


    def test_defaults(self):
        """
        Тест виджетов тестовой формы
        """
        self.testForm = pyqt_signals.TestForm()

        testTableHeader = ["Параметр", "Значение"]

        testTableData = [
            ["Signal 1", ""],
            ["Signal 2", ""],
            ["Signal 3", ""],
        ]

        # проверить количество строк в таблице
        self.assertEqual( self.getRowCount(), len(testTableData) )
        # проверить количество столбцов в таблице
        self.assertEqual( self.getColumnCount(), len(testTableData[0]) )

        # проверить заголовки столбцов в таблице
        self.assertEqual( self.getTableHeader(), testTableHeader )

        # сравнить данные таблицы с тестовыми
        self.assertEqual( self.getTableData(), testTableData )
        # сравнить значения полей формы с тестовыми
        self.assertEqual( self.getLabelsLines(), testTableData )


    def test_setParam(self):
        """
        Тест установки значения параметра в поля тестовой формы
        """
        self.testForm = pyqt_signals.TestForm()

        testParams = [
            ["Signal 1", "12"],
            ["Signal 2", "34"],
            ["Signal 3", "56"],
        ]

        # установить тестовые параметры в поля формы
        for paramName, paramValue in testParams:
            self.testForm.setParam(paramName, paramValue)

        # сравнить данные таблицы с тестовыми
        self.assertEqual( self.getTableData(), testParams )
        # сравнить значения полей формы с тестовыми
        self.assertEqual( self.getLabelsLines(), testParams )


if __name__ == "__main__":
    unittest.main()

