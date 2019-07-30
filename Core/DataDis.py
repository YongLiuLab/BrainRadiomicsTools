from UI import dataUI
from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox
import os
from Core.Report import reportBuild
class DataWindow(QWidget,dataUI.Ui_BrainExtraction):
    def __init__(self,parent=None):
        super(DataWindow,self).__init__(parent)
        self.setupUi(self)
        self.btnBrainSegPath.clicked.connect(self.chooseBrain)
        self.btnFeaturePath.clicked.connect(self.chooseFeature)
        self.btnHippoPath.clicked.connect(self.chooseHippo)
        self.btnImagePath.clicked.connect(self.chooseImage)
        self.BtnChooseOutput.clicked.connect(self.outputFile)
        self.dirPath = "../../"
        self.BtnStart.clicked.connect(self.calData)
    def chooseImage(self):
        self.dirPath, ok = QFileDialog.getOpenFileName(self, "Open File", self.dirPath,
                                                             "Nii File (*.nii);;Nii.gz (*.nii.gz)")
        self.imageFile = self.dirPath
        self.dirPath = os.path.dirname(self.dirPath)
        self.lineImagePath.setText(self.imageFile)

    def chooseBrain(self):
        self.dirPath = QFileDialog.getExistingDirectory(self,"Choose DIR " ,self.dirPath)

        self.brainDIR = self.dirPath

        self.LineBrainPath.setText(self.brainDIR)

    def chooseFeature(self):
        self.dirPath, ok = QFileDialog.getOpenFileName(self, "Open File", self.dirPath,
                                                       "Csv File (*.csv)")

        self.FeaturePath = self.dirPath
        self.dirPath = os.path.dirname(self.dirPath)

        self.LineFeaturePath.setText(self.FeaturePath)

    def chooseHippo(self):
        self.HippoPath, ok = QFileDialog.getOpenFileName(self, "Open File", self.dirPath,
                                                         "Nii File (*.nii);;Nii.gz (*.nii.gz)")

        self.dirPath = os.path.dirname(self.HippoPath)

        self.LineHippo.setText(self.HippoPath)

    def outputFile(self):
        self.outputPath = QFileDialog.getExistingDirectory(self, "Choose DIR", self.dirPath)
        self.LineOutput.setText(self.outputPath)

    def calData(self):
        from Core.utils import checkDir,checkFile
        if len(checkDir(self.brainDIR)) == 0:
            QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
            return
        brains = os.listdir(self.brainDIR)
        wmPath = ""
        gmPath =""
        csfPath=""
        for brain in brains:
            if(brain.find('wm')!=-1):
                wmPath = os.path.join(self.brainDIR,brain)
            elif(brain.find("csf")!=-1):
                csfPath = os.path.join(self.brainDIR,brain)
            elif(brain.find("gm")!=-1):
                gmPath = os.path.join(self.brainDIR,brain)
        if(wmPath == "" or gmPath == "" or csfPath== ""):
            QMessageBox.information(self, "Warning", "The brain segmentation path is not valid!", QMessageBox.Yes)
            return
        self.thread = calThread(self.FeaturePath,wmPath,gmPath,csfPath,self.HippoPath,self.imageFile,self.outputPath)
        self.thread.signal.connect(self.precess)
        self.thread.start()
        self.BtnStart.setDisabled(True)

    def precess(self,p):
        if (p == 1):
            QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
        else:
            QMessageBox.information(self, "Error ", "Calculate exit with error!", QMessageBox.Yes)
        self.BtnStart.setDisabled(False)
from PyQt5.QtCore import QThread, pyqtSignal
class calThread(QThread):
    signal = pyqtSignal(int)

    def __init__(self, featurePath,wmPath,gmPath,csfPath,hippoPath,originImagePath,tempDir):
        super(calThread, self).__init__()
        self.featurePath = featurePath
        self.wmPath = wmPath
        self.gmPath = gmPath
        self.csfPath = csfPath
        self.hippoPath = hippoPath
        self.originImagePath = originImagePath
        self.tempDir = tempDir

    def run(self):
        try:
            reportBuild(self.featurePath,self.wmPath,self.gmPath,self.csfPath,self.hippoPath,self.originImagePath,self.tempDir)
        except Exception:
            self.signal.emit(2)
            return
        self.signal.emit(1)
