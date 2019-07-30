from UI import bfcUI
from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox
from Core.N4Correct import N4correctBatch,N4correct,N4correctWin
from Core.utils import checkFile,checkDir
class BFCwindow(QWidget,bfcUI.Ui_BrainExtraction):
    def __init__(self,parent=None):
        super(BFCwindow,self).__init__(parent)
        self.setupUi(self)
        self.BtnChooseFile.clicked.connect(self.chooseImage)
        self.BtnChooseOutput.clicked.connect(self.outputFile)
        self.BtnStart.clicked.connect(self.cal)
        self.RadioSingle.setChecked(True)
        self.CheckBFC.setChecked(True)
        self.CheckNorm.setChecked(True)

    def chooseImage(self):
        if self.RadioSingle.isChecked():
            self.imageFile, ok = QFileDialog.getOpenFileName(self, "Open File", "../",
                                                             "Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineFile.setText(self.imageFile)
        else:
            self.imageFile = QFileDialog.getExistingDirectory(self, "Choose DIR", "../")
            self.LineFile.setText(self.imageFile)

    def outputFile(self):
        if self.RadioSingle.isChecked():
            self.outputPath, ok = QFileDialog.getSaveFileName(self, "Save File", "../",
                                                              "Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineOutput.setText(self.outputPath)
        else:
            self.outputPath = QFileDialog.getExistingDirectory(self, "Choose DIR", "../")
            self.LineOutput.setText(self.outputPath)

    def cal(self):
        if((not self.CheckNorm) and (not self.CheckBFC)):
            QMessageBox.information(self, "Warning", "Please Choose at least one function!", QMessageBox.Yes)
            return
        if self.RadioSingle.isChecked():
            if checkFile(self.imageFile) == 1:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        else:
            if len(checkDir(self.imageFile)) == 0:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        self.thread = calThread(self.imageFile, self.outputPath, self.CheckBFC.isChecked(),self.CheckNorm.isChecked(),self.RadioSingle.isChecked())
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

class calThread(QThread):
    signal = pyqtSignal(float)

    def __init__(self, input, output, isBFC, isNorm ,isSingleFile):
        super(calThread, self).__init__()
        self.inputPath = input
        self.outputPath = output
        self.isBFC = isBFC
        self.isNorm = isNorm
        self.isSingleFile = isSingleFile
    def run(self):
        try:
            if(self.isSingleFile):
                N4correctWin(self.inputPath, self.outputPath, isNorm=self.isNorm,isBFC=self.isBFC)
            else:
                N4correctBatch(self.inputPath,self.outputPath,isNormal=self.isNorm,isBFC=self.isBFC)
        except Exception:
            self.signal.emit(2)
        self.signal.emit(1)
