# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_segment.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(438, 189)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.input_label = QtWidgets.QLabel(Dialog)
        self.input_label.setGeometry(QtCore.QRect(30, 60, 72, 15))
        self.input_label.setObjectName("input_label")
        self.output_label = QtWidgets.QLabel(Dialog)
        self.output_label.setGeometry(QtCore.QRect(30, 100, 72, 16))
        self.output_label.setObjectName("output_label")
        self.input_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.input_lineEdit.setGeometry(QtCore.QRect(90, 60, 271, 21))
        self.input_lineEdit.setObjectName("input_lineEdit")
        self.output_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.output_lineEdit.setGeometry(QtCore.QRect(90, 100, 271, 21))
        self.output_lineEdit.setObjectName("output_lineEdit")
        self.input_pushButton = QtWidgets.QPushButton(Dialog)
        self.input_pushButton.setGeometry(QtCore.QRect(380, 60, 31, 28))
        self.input_pushButton.setObjectName("input_pushButton")
        self.output_pushButton = QtWidgets.QPushButton(Dialog)
        self.output_pushButton.setGeometry(QtCore.QRect(380, 100, 31, 28))
        self.output_pushButton.setObjectName("output_pushButton")
        self.run_pushButton = QtWidgets.QPushButton(Dialog)
        self.run_pushButton.setGeometry(QtCore.QRect(170, 140, 93, 28))
        self.run_pushButton.setObjectName("run_pushButton")
        self.RadioBtn_File = QtWidgets.QRadioButton(Dialog)
        self.RadioBtn_File.setGeometry(QtCore.QRect(30, 20, 89, 16))
        self.RadioBtn_File.setObjectName("RadioBtn_File")
        self.buttonGroup_2 = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.RadioBtn_File)
        self.RadioBtn_Dir = QtWidgets.QRadioButton(Dialog)
        self.RadioBtn_Dir.setGeometry(QtCore.QRect(280, 20, 131, 16))
        self.RadioBtn_Dir.setObjectName("RadioBtn_Dir")
        self.buttonGroup_2.addButton(self.RadioBtn_Dir)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Segment"))
        self.input_label.setText(_translate("Dialog", "Input"))
        self.output_label.setText(_translate("Dialog", "Output"))
        self.input_pushButton.setText(_translate("Dialog", "..."))
        self.output_pushButton.setText(_translate("Dialog", "..."))
        self.run_pushButton.setText(_translate("Dialog", "Run"))
        self.RadioBtn_File.setText(_translate("Dialog", "SingleFile"))
        self.RadioBtn_Dir.setText(_translate("Dialog", "Director Batch"))

