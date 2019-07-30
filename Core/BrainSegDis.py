from UI import bfcUI
from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox,QPushButton
from Core.utils import checkDir,checkFile
class BrinSegwindow(QWidget,bfcUI.Ui_BrainExtraction):
    def __init__(self,parent=None):
        super(BrinSegwindow,self).__init__(parent)


        self.setupUi(self)
        self.setWindowTitle("Brain Segmentation")
        #self.horizontalLayout_4.removeWidget(self.CheckBFC)
        self.CheckBFC.deleteLater()
        self.CheckNorm.deleteLater()
        self.BtnChooseFile.clicked.connect(self.chooseImage)
        self.BtnChooseOutput.clicked.connect(self.outputFile)
        self.BtnStart.clicked.connect(self.cal)
        self.RadioSingle.setChecked(True)
        self.imageFile = None
        self.outputPath = '../'
    def chooseImage(self):
        if self.RadioSingle.isChecked():
            self.imageFile, ok = QFileDialog.getOpenFileName(self, "Open File", self.outputPath,
                                                             "Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineFile.setText(self.imageFile)
        else:
            self.imageFile = QFileDialog.getExistingDirectory(self, "Choose DIR", self.outputPath)
            self.LineFile.setText(self.imageFile)

    def outputFile(self):
        if self.RadioSingle.isChecked():
            self.outputPath = QFileDialog.getExistingDirectory(self, "Choose DIR", self.outputPath)
            self.LineOutput.setText(self.outputPath)
        else:
            self.outputPath = QFileDialog.getExistingDirectory(self, "Choose DIR", self.outputPath)
            self.LineOutput.setText(self.outputPath)

    def cal(self):
        if self.RadioSingle.isChecked():
            if checkFile(self.imageFile) == 1:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        else:
            if len(checkDir(self.imageFile)) == 0:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        if((self.imageFile is None) and (self.outputPath is None)):
            QMessageBox.information(self, "Warning", "Please Choose the path!", QMessageBox.Yes)
            return
        self.thread = calThread(self.imageFile, self.outputPath,self.RadioSingle.isChecked())
        self.thread.signal.connect(self.process)
        self.thread.start()
        self.BtnStart.setDisabled(True)
        self.BtnStart.setText("Calculating...")
    def process(self, p):
        self.BtnStart.setDisabled(False)
        self.BtnStart.setText("reStart")
        if(p==1):
            QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
        else:
            QMessageBox.information(self, "Error ", "Calculate exit with error!", QMessageBox.Yes)

from PyQt5.QtCore import QThread, pyqtSignal
import os
import numpy as np
from Core.brainSeg import runSeg
class calThread(QThread):
    signal = pyqtSignal(float)

    def __init__(self, input, output,isSingleFile):
        super(calThread, self).__init__()
        self.inputPath = input
        self.outputPath = output
        self.isSingleFile = isSingleFile
    def run(self):
        try:
            if(self.isSingleFile):
                runSeg.runSeg(self.inputPath, self.outputPath)
            else:
                runSeg.batchSeg(self.inputPath,self.outputPath)
        except Exception as e:
            print(e)
            self.signal.emit(2)
            return
        self.signal.emit(1)