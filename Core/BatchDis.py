from UI import batchUI
from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox,QHeaderView,QTableWidgetItem,QTableWidget
import os
from Core.batch import batchCal
import numpy as np
class Batchwindow(QWidget,batchUI.Ui_Form):
    def __init__(self,parent=None):
        super(Batchwindow,self).__init__(parent)
        self.setupUi(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.table.horizontalHeader().resizeSection(1, 50)
        # self.regCheckBox.setChecked(False)
        # self.betCheckBox.setChecked(True)
        # self.HsCheckBox.setChecked(True)
        # self.BsCheckBox_2.setChecked(True)
        # self.FeatureCheckBox.setChecked(True)
        # self.N4CheckBox.setChecked(True)

        #self.dicomCheckBox.clicked.connect(self.callbackCheck)
        self.regCheckBox.clicked.connect(self.callbackCheck)
        self.betCheckBox.clicked.connect(self.callbackCheck)
        self.N4CheckBox.clicked.connect(self.callbackCheck)
        self.HsCheckBox.clicked.connect(self.callbackCheck)
        self.BsCheckBox_2.clicked.connect(self.callbackCheck)
        self.FeatureCheckBox.clicked.connect(self.callbackCheck)
        self.dataCheckBox_2.clicked.connect(self.callbackCheck)


        self.PreprocessingcheckBox.clicked.connect(self.autoCheck)
        self.SegCheckBox.clicked.connect(self.autoCheck)
        self.AnalysisCheckBox.clicked.connect(self.autoCheck)

        self.chooseInputButton.clicked.connect(self.chooseDir)
        self.chooseOutputButton.clicked.connect(self.chooseOutputDir)
        self.dir = "../"
        self.outputDir = "../"
        self.startButton.clicked.connect(self.cal)

        self.autoCheck()
    def callbackCheck(self):
        #self.ifCheck(self.dicomCheckBox,self.dicomLabel)
        #self.autoCheck()

        self.ifCheck(self.regCheckBox,self.regLabel)
        self.ifCheck(self.betCheckBox,self.betLabel)
        self.ifCheck(self.N4CheckBox,self.N4Label)
        self.ifCheck(self.HsCheckBox,self.betLabel_2)
        self.ifCheck(self.FeatureCheckBox,self.FeatureLabel)
        self.ifCheck(self.dataCheckBox_2,self.dataLabel_2)
        self.ifCheck(self.BsCheckBox_2,self.segLabel)

        if(self.regCheckBox.isChecked() and self.betCheckBox.isChecked() and self.N4CheckBox.isChecked()):
            self.PreprocessingcheckBox.setChecked(True)
        else:
            self.PreprocessingcheckBox.setChecked(False)

        if(self.HsCheckBox.isChecked() and self.BsCheckBox_2.isChecked()):
            self.SegCheckBox.setChecked(True)
        else:
            self.SegCheckBox.setChecked(False)
        
        if( self.dataCheckBox_2.isChecked() ):
            self.AnalysisCheckBox.setChecked(True)

            self.HsCheckBox.setDisabled(True)
            self.HsCheckBox.setChecked(True)
            
            self.BsCheckBox_2.setChecked(True)
            self.BsCheckBox_2.setDisabled(True)

            self.FeatureCheckBox.setChecked(True)
            self.FeatureCheckBox.setDisabled(True)
        else:
            self.AnalysisCheckBox.setChecked(False)
            self.FeatureCheckBox.setDisabled(False)
            self.BsCheckBox_2.setDisabled(False)

        if(self.FeatureCheckBox.isChecked()):
            self.HsCheckBox.setChecked(True)
            self.HsCheckBox.setDisabled(True)
        else:
            self.HsCheckBox.setDisabled(False)
        

        if(self.HsCheckBox.isChecked() or self.BsCheckBox_2.isChecked()):
            self.PreprocessingcheckBox.setChecked(True)
            self.PreprocessingcheckBox.setDisabled(True)
            self.PreprocessCheck()
        else:
            self.PreprocessingcheckBox.setDisabled(False)

        
    # 检测 checkbox 的状态来改变前方label的颜色
    def autoCheck(self):
        print("Checing")
        if(self.AnalysisCheckBox.isChecked()):
            self.SegCheckBox.setChecked(True)
            self.SegCheckBox.setDisabled(True)

            self.FeatureCheckBox.setChecked(True)
            self.FeatureCheckBox.setDisabled(True)

            self.dataCheckBox_2.setChecked(True)
            self.dataCheckBox_2.setDisabled(True)
        else:
            self.SegCheckBox.setDisabled(False)
            self.FeatureCheckBox.setChecked(False)
            self.FeatureCheckBox.setDisabled(False)

            self.dataCheckBox_2.setChecked(False)
            self.dataCheckBox_2.setDisabled(False)

        if(self.SegCheckBox.isChecked()):
            self.PreprocessingcheckBox.setChecked(True)
            self.PreprocessingcheckBox.setDisabled(True)

            self.HsCheckBox.setChecked(True)
            #self.HsCheckBox.setDisabled(True)

            self.BsCheckBox_2.setChecked(True)
            #self.BsCheckBox_2.setDisabled(True)
        else:
            self.PreprocessingcheckBox.setDisabled(False)
            self.HsCheckBox.setChecked(False)
            self.HsCheckBox.setDisabled(False)

            self.BsCheckBox_2.setChecked(False)
            self.BsCheckBox_2.setDisabled(False)


        if(self.PreprocessingcheckBox.isChecked()):
            self.regCheckBox.setChecked(True)
            self.regCheckBox.setDisabled(True)
            
            self.betCheckBox.setChecked(True)
            self.betCheckBox.setDisabled(True)
            
            self.N4CheckBox.setChecked(True)
            self.N4CheckBox.setDisabled(True)
        else:
            self.regCheckBox.setChecked(False)
            self.regCheckBox.setDisabled(False)
            
            self.betCheckBox.setChecked(False)
            self.betCheckBox.setDisabled(False)
            
            self.N4CheckBox.setChecked(False)
            self.N4CheckBox.setDisabled(False)
        
        self.callbackCheck()
        
    #control the label color
    def PreprocessCheck(self):
        if(self.PreprocessingcheckBox.isChecked()):
            self.regCheckBox.setChecked(True)
            self.regCheckBox.setDisabled(True)
            
            self.betCheckBox.setChecked(True)
            self.betCheckBox.setDisabled(True)
            
            self.N4CheckBox.setChecked(True)
            self.N4CheckBox.setDisabled(True)
        else:
            self.regCheckBox.setChecked(False)
            self.regCheckBox.setDisabled(False)
            
            self.betCheckBox.setChecked(False)
            self.betCheckBox.setDisabled(False)
            
            self.N4CheckBox.setChecked(False)
            self.N4CheckBox.setDisabled(False)
    def ifCheck(self,checkBox,label):
        if (checkBox.isChecked()):
            self.labelCheck(label)
        else:
            self.labelUnCheck(label)
    def labelCheck(self,label):
        label.setStyleSheet("background:green;")
    def labelUnCheck(self,label):
        label.setStyleSheet("background:gray;")
    def Check(self):
        pass
    def chooseOutputDir(self):
        self.outputDir = QFileDialog.getExistingDirectory(self, "Choose DIR", self.dir)
        if self.outputDir == "":
            return
        self.label_2.setText(self.outputDir)
        
    def chooseDir(self):
        self.dir = QFileDialog.getExistingDirectory(self, "Choose DIR", self.dir)
        if self.dir == "":
            return
        self.label.setText(dir)
        files = os.listdir(self.dir)
        self.images = []
        for f in files:
            if f.split(".")[-1] == "nii" or f.split(".")[-2:0] == 'nii.gz':
                self.images.append(f)
        self.table.setRowCount(len(self.images))
        self.proImages = []
        for image,i in zip(self.images,range(len(self.images))):
            tmp = []
            tmp.append(QTableWidgetItem(str(image.split(".")[0])))
            tmp.append(QTableWidgetItem("Waiting"))
            tmp.append(QTableWidgetItem(os.path.join(self.dir,image)))
            self.table.setItem(i, 0, tmp[0])
            self.table.setItem(i, 1, tmp[1])
            self.table.setItem(i, 2, tmp[2])
            self.proImages.append(tmp)
        #QTableWidget.resizeColumnsToContents(self.table)
    def cal(self):

        if len(self.images)== 0:
            QMessageBox.information(self, "Warning", "The path is not valid!", QMessageBox.Yes)
            return
        if self.outputDir == "../" :
            QMessageBox.information(self, "Warning", "Please choose output path", QMessageBox.Yes)
            return
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        self.outputDir = os.path.join(self.outputDir,"BRT_OUTPUT")
        self.calthread = batchCal(self.dir,
                                  self.images,
                                  self.outputDir,
                                  self.regCheckBox.isChecked(),
                                  self.N4CheckBox.isChecked(),
                                  self.betCheckBox.isChecked(),
                                  self.HsCheckBox.isChecked(),
                                  self.BsCheckBox_2.isChecked(),
                                  self.FeatureCheckBox.isChecked(),
                                  self.dataCheckBox_2.isChecked())
        self.calthread.signal.connect(self.progress)
        self.calthread.strSignal.connect(self.progressDis)
        self.calthread.fileSignal.connect(self.progressFile)
        self.calthread.start()
        self.startButton.setDisabled(True)
    def progress(self,p):
        print("complete task :",p)
        check = [ self.regCheckBox.isChecked(),
                self.betCheckBox.isChecked(),
                self.N4CheckBox.isChecked(),
                self.HsCheckBox.isChecked(),
                self.FeatureCheckBox.isChecked(),
                self.dataCheckBox_2.isChecked(),
                  self.BsCheckBox_2.isChecked()]
        check = np.array(check)
        taskNum = len(check[check == True])
        print("all taskNUm:",taskNum)
        pn = int(p / taskNum * 100)
        print("percent :",pn)
        self.progressBar.setValue(pn)
        if(p == 100):
            QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
            self.runLabel.setText("Calculate Done !")
            self.startButton.setDisabled(False)
        elif(p==-1):
            QMessageBox.information(self,"Waring","Calculate Failed!",QMessageBox.Yes)
            self.runLabel.setText("Calculate Failed !")
            self.startButton.setDisabled(False)
            self.progressBar.setValue(0)
    def progressDis(self,p):
        print("progressDiss:",p)
        self.runLabel.setText(p)
    def progressFile(self,p):
        self.table.setItem(int(p), 1, QTableWidgetItem("Complete"))

