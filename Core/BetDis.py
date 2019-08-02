from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox
from UI import betUI
from Core.setting import selectRootPath
class BetWindow(QWidget,betUI.Ui_BrainExtraction):
    def __init__(self,parent=None):
        super(BetWindow,self).__init__(parent)
        self.setupUi(self)
        self.BtnChooseFile.clicked.connect(self.chooseImage)
        self.BtnChooseOutput.clicked.connect(self.outputFile)
        self.BtnStart.clicked.connect(self.cal)
        self.RadioSingle.setChecked(True)
        self.RadioFast.setChecked(True)
        
        self.LineFile.setDisabled(True)
        self.LineOutput.setDisabled(True)
        self.imageFile = selectRootPath
        self.outputPath = selectRootPath
    def chooseImage(self):
        if self.RadioSingle.isChecked():
            self.imageFile,ok = QFileDialog.getOpenFileName(self,"Open File","../","Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineFile.setText(self.imageFile)
        else:
            self.imageFile = QFileDialog.getExistingDirectory(self, "Choose DIR", "../")
            self.LineFile.setText(self.imageFile)
    def outputFile(self):
        if self.RadioSingle.isChecked():
            self.outputPath,ok = QFileDialog.getSaveFileName(self,"Save File","../","Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineOutput.setText(self.outputPath)
        else:
            self.outputPath = QFileDialog.getExistingDirectory(self, "Choose DIR", "../")
            self.LineOutput.setText(self.outputPath)
    def cal(self):
        '''
        这里hd-bet内部自动会判断输入的是文件夹/文件，故没有判断
        :return:
        '''
        from Core.utils import checkDir,checkFile,checkOutputFile,checkOutputDir
        if self.RadioSingle.isChecked():
            if (checkFile(self.imageFile) == 1 or checkOutputFile(self.outputPath) == 1):
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        else:
            if (len(checkDir(self.imageFile)) == 0 or checkOutputDir(self.outputPath) == 1):
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        self.thread = calThread(self.imageFile,self.outputPath,self.RadioFast.isChecked())
        self.thread.signal.connect(self.process)
        self.thread.start()
        self.BtnStart.setDisabled(True)
        self.BtnStart.setText("Calculating...")
    def process(self,p):
        self.BtnStart.setDisabled(False)
        self.BtnStart.setText("reStart")
        QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
from PyQt5.QtCore import QThread,pyqtSignal
class calThread(QThread):
    signal = pyqtSignal(float)
    def __init__(self,input,output,mode):
        super(calThread, self).__init__()
        self.inputPath = input
        self.outputPath = output
        self.mode = mode
    def run(self):
        from Core.bet import Bet

        #Bet.BrainExtract(self.inputPath, self.outputPath,mode=self.mode)
        print("Brain Extraction Input Path :",self.inputPath)
        print("Brain Extraction Output Path :",self.outputPath)
        Bet.BrainExtractFast(self.inputPath,self.outputPath)
        self.signal.emit(1)