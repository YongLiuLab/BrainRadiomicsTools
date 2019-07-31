
from UI import dicomUI
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread,pyqtSignal
from Core.dicom2nii import convertDicoms
class DicomWindow(QWidget, dicomUI.Ui_Form):
    def __init__(self,parent=None):
        super(DicomWindow,self).__init__(parent)
        self.setupUi(self)
    def DicomDir(self):
        self.directory1 = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose DIR", "./")
        self.dicomLt.setText(self.directory1)
    def NiiDir(self):
        self.niiFile,ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "./","nii Files (*.nii)")
        self.niiLt.setText(self.niiFile)
    def Cal(self):
        if(self.directory1 is None or self.niiFile is None):
            QtWidgets.QMessageBox.information(self, "Warning", "the path is not corrected!", QtWidgets.QMessageBox.Yes)
            return
        self.startBtn.setDisabled(True)
        self.thread = calculate(self.directory1, self.niiFile)
        self.thread.start()
        self.thread.signal.connect(self.show_message)
    def show_message(self,p):
        if p==0:
            QtWidgets.QMessageBox.information(self, "Information", "Calculate Done!", QtWidgets.QMessageBox.Yes)
        else:
            QtWidgets.QMessageBox.information(self, "Information", "Calculate Error!", QtWidgets.QMessageBox.Yes)
        self.startBtn.setDisabled(False)
class calculate(QThread):
    signal = pyqtSignal(float)

    def __init__(self,directory1,niiFile):
        super(calculate, self).__init__()
        self.director1 = directory1
        self.niiFile = niiFile
    def __del__(self):
        self.wait()

    def run(self):

        p = convertDicoms(self.director1,self.niiFile)
        self.signal.emit(p)
        # self._signal.emit(msg)

    def callback(self, msg):
        # self._signal.emit(msg)
        pass
