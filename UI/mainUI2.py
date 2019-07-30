# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUI2.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
from segment import Segment
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(406, 402)
        MainWindow.setStyleSheet("#frame{border:none}\n"
"centralwidget{background-color: white}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 391, 351))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TopFrame = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.TopFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.TopFrame.setStyleSheet("")
        self.TopFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.TopFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.TopFrame.setObjectName("TopFrame")
        self.frame = QtWidgets.QFrame(self.TopFrame)
        self.frame.setGeometry(QtCore.QRect(20, 10, 361, 91))
        self.frame.setStyleSheet("background: url(:/icon2/b.png);\n"
"background-repeat:none;\n"
"background-width:cover;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout.addWidget(self.TopFrame)
        self.middleFrame = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.middleFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.middleFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.middleFrame.setObjectName("middleFrame")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.middleFrame)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 391, 111))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(20, 0, 20, 0)
        self.horizontalLayout.setSpacing(40)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BtnDicom = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.BtnDicom.setMinimumSize(QtCore.QSize(0, 50))
        self.BtnDicom.setObjectName("BtnDicom")
        self.horizontalLayout.addWidget(self.BtnDicom)
        self.BtnReg = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.BtnReg.setMinimumSize(QtCore.QSize(0, 50))
        self.BtnReg.setObjectName("BtnReg")
        self.horizontalLayout.addWidget(self.BtnReg)
        self.verticalLayout.addWidget(self.middleFrame)
        self.BottomFrame = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.BottomFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BottomFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BottomFrame.setObjectName("BottomFrame")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.BottomFrame)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, -10, 391, 141))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(20, 0, 20, 0)
        self.horizontalLayout_2.setSpacing(40)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.BtnSeg = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.BtnSeg.setMinimumSize(QtCore.QSize(0, 50))
        self.BtnSeg.setObjectName("BtnSeg")
        self.horizontalLayout_2.addWidget(self.BtnSeg)
        self.BtnFeature = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.BtnFeature.setMinimumSize(QtCore.QSize(0, 50))
        self.BtnFeature.setObjectName("BtnFeature")
        self.horizontalLayout_2.addWidget(self.BtnFeature)
        self.verticalLayout.addWidget(self.BottomFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 406, 23))
        self.menubar.setObjectName("menubar")
        self.menuabout = QtWidgets.QMenu(self.menubar)
        self.menuabout.setObjectName("menuabout")
        self.menuhelp = QtWidgets.QMenu(self.menubar)
        self.menuhelp.setObjectName("menuhelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionversion = QtWidgets.QAction(MainWindow)
        self.actionversion.setObjectName("actionversion")
        self.actionhelo = QtWidgets.QAction(MainWindow)
        self.actionhelo.setObjectName("actionhelo")
        self.menuabout.addAction(self.actionversion)
        self.menuhelp.addAction(self.actionhelo)
        self.menubar.addAction(self.menuabout.menuAction())
        self.menubar.addAction(self.menuhelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BrainToolBox"))
        self.BtnDicom.setText(_translate("MainWindow", "Dicom2nii"))
        self.BtnReg.setText(_translate("MainWindow", "Registration"))
        self.BtnSeg.setText(_translate("MainWindow", "Segmentation"))
        self.BtnFeature.setText(_translate("MainWindow", "Feature"))
        self.menuabout.setTitle(_translate("MainWindow", "about"))
        self.menuhelp.setTitle(_translate("MainWindow", "help"))
        self.actionversion.setText(_translate("MainWindow", "version"))
        self.actionhelo.setText(_translate("MainWindow", "help"))

from . import resource_rc
from . import res