#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow


class CoffeeInfoChanger(QDialog):

    def __init__(self, other, kind_name=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.kind_name = kind_name
        self.other = other
        self.connection = sqlite3.connect("coffee.sqlite")
        self.cursor = self.connection.cursor()
        self.initUI()

    # noinspection PyPep8Naming
    def initUI(self):
        if self.kind_name is not None:
            sql_command = f"""SELECT * FROM coffee 
                              WHERE kind_name = '{self.kind_name}'"""
            res = self.connection.cursor().execute(sql_command).fetchone()
            self.lineEdit_kind_name.setText(f'{res[1]}')
            self.lineEdit_roast.setText(f'{res[2]}')
            self.lineEdit_ground_or_in_grains.setText(f'{res[3]}')
            self.lineEdit_taste.setText(f'{res[4]}')
            self.lineEdit_price.setText(f'{res[5]}')
            self.lineEdit_volume.setText(f'{res[6]}')
        self.pushButton_apply.clicked.connect(self.change_coffee_info)

    def change_coffee_info(self):
        if not self.lineEdit_kind_name.text() or \
                not self.lineEdit_roast.text() or \
                not self.lineEdit_ground_or_in_grains.text() or \
                not self.lineEdit_taste.text() or \
                not self.lineEdit_price.text() or \
                not self.lineEdit_volume.text():
            QMessageBox.critical(self, "Ошибка!",
                                 'Поажалуйста, заполните все поля.',
                                 QMessageBox.Ok)
            return
        if self.kind_name is not None:
            sql_command = f"""UPDATE coffee 
            SET kind_name = '{self.lineEdit_kind_name.text()}', 
            roast = '{self.lineEdit_roast.text()}', 
            ground_or_in_grains = '{self.lineEdit_ground_or_in_grains.text()}', 
            taste = '{self.lineEdit_taste.text()}', 
            price = {self.lineEdit_price.text()},
            volume = {self.lineEdit_volume.text()}
            WHERE kind_name = '{self.kind_name}'"""
        else:
            sql_command = f"""INSERT INTO coffee 
            (kind_name, roast, ground_or_in_grains, taste, price, volume)
            VALUES ('{self.lineEdit_kind_name.text()}', 
            '{self.lineEdit_roast.text()}', 
            '{self.lineEdit_ground_or_in_grains.text()}', 
            '{self.lineEdit_taste.text()}', 
            {self.lineEdit_price.text()}, 
            {self.lineEdit_volume.text()})"""
        # noinspection PyBroadException
        try:
            self.connection.cursor().execute(sql_command)
        except Exception:
            QMessageBox.critical(self, "Ошибка!",
                                 'Невозможно добавить введённые значения.\n'
                                 'Поажалуйста, проверьте корректность ввода.',
                                 QMessageBox.Ok)
            return
        self.connection.commit()
        self.hide()
        self.other.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.pushButton_apply.click()

    def closeEvent(self, event):
        # При закрытии формы закроем соединение с базой данных.
        self.connection.close()


class CoffeeInfoViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect("coffee.sqlite")
        self.cursor = self.connection.cursor()
        self.widget = None
        self.initUI()

    # noinspection PyPep8Naming
    def initUI(self):
        sql_command = """SELECT * FROM coffee"""
        res = self.connection.cursor().execute(sql_command).fetchall()
        if not res:
            QMessageBox.warning(self, "Информация о результате.",
                                'К сожалению, ничего не нашлось.',
                                QMessageBox.Ok)
        # Заполним размеры таблицы.
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами.
        self.tableWidget.setHorizontalHeaderLabels(
            ['ID', 'Название сорта', 'Степень обжарки', 'Молотый / в зёрнах',
             'Описание вкуса', 'Цена', 'Объём упаковки'])
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.selectRow(0)
        self.pushButton_add_info.clicked.connect(self.open_widget)
        self.pushButton_chang_info.clicked.connect(self.open_widget)

    def open_widget(self):
        if self.sender().text() == 'Редактировать информацию о кофе':
            self.widget = CoffeeInfoChanger(self,
                                            kind_name=self.tableWidget.item(
                                                self.tableWidget.currentRow(),
                                                1).text())
        else:
            self.widget = CoffeeInfoChanger(self)
        self.widget.setFixedSize(self.widget.width(), self.widget.height())
        self.widget.setWindowModality(Qt.ApplicationModal)
        self.widget.show()

    def closeEvent(self, event):
        # При закрытии формы закроем соединение с базой данных.
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeInfoViewer()
    ex.show()
    sys.exit(app.exec_())
