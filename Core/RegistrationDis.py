# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox, QWidget,  QFileDialog
from PyQt5.QtCore import QThread,pyqtSignal
from Core.registration import registration
from UI import regUI
from Core.setting import selectRootPath
from Core.utils import checkDir
import os
class RegWindow(QWidget,regUI.Ui_Form):
    def __init__(self,parent=None):
        super(RegWindow,self).__init__(parent)
        self.setupUi(self)
        self.BtnImage.clicked.connect(self.ImageSelect)
        self.BtnImage_2.clicked.connect(self.RefSelect)
        self.BtnResult.clicked.connect(self.ResSelect)
        self.RdioSingleFile.setChecked(True)
        self.BtnStart.clicked.connect(self.Cal)
        self.RefImage = None
        self.LineRef.setDisabled(True)
        self.LineResult.setDisabled(True)
        self.LineImage.setDisabled(True)
        self.selectRoot = selectRootPath 

        self.imagePath = self.selectRoot
    def ImageSelect(self):
        if self.RdioSingleFile.isChecked():

            self.imagePath,ok = QFileDialog.getOpenFileName(self,"Open File",self.selectRoot,"Nii File (*.nii);;Nii.gz (*.nii.gz)")
            
            if(self.imagePath != ""):
                self.selectRoot = os.path.dirname(self.Image)

            self.LineImage.setText(self.imagePath)
        else:
            self.imagePath = QFileDialog.getExistingDirectory(self, "Choose DIR", self.selectRoot)
            if(self.imagePath !=""):
                self.selectRoot = self.imagePath
            
            self.LineImage.setText(self.imagePath)
    def RefSelect(self):
        self.refImagePath, ok = QFileDialog.getOpenFileName(self, "Open File", self.selectRoot,
                                                         "Nii File (*.nii);;Nii.gz (*.nii.gz)")
        
        if(self.refImagePath != ""):
            self.selectRoot = os.path.dirname(self.refImagePath)
        
        self.LineRef.setText(self.refImagePath)
    def ResSelect(self):
        if self.RdioSingleFile.isChecked():
            self.ResImage,ok = QFileDialog.getSaveFileName(self, "Save File", "../","Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.LineResult.setText(self.ResImage)
        else:
            self.directory2 = QFileDialog.getExistingDirectory(self, "Choose DIR", "./")
            self.LineResult.setText(self.directory2)
    def Cal(self):

        from Core.utils import checkFile,checkDir
        if self.RdioSingleFile.isChecked():
            if checkFile(self.Image) == 1:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
            self.thread = calculate(self.Image, self.RefImage ,self.ResImage )
        else:
            if len(checkDir(self.directory1)) == 0:
                QMessageBox.information(self, "Warning", "The directory path is not valid!", QMessageBox.Yes)
                return
            self.thread = calculate(self.directory1,self.RefImage,self.directory2,type=1)
        self.BtnStart.setDisabled(True)
        self.thread.start()
        self.thread.signal.connect(self.process)
    def process(self,p):
        if p<=1:
            p=p*100
        self.ProcessBar.setValue(p)
        if (p == 100):
            self.BtnStart.setText("ReStart!")
            self.BtnStart.setDisabled(False)
            self.show_message()
    def show_message(self):
        QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
#计算线程，调用registration函数进行计算
class calculate(QThread):

    signal = pyqtSignal(float)
    def __init__(self,image,refImage,resImage,type=0):
        '''

        :param image:
        :param refImage:
        :param resImage:
        :param type: int 0 -> singleFile 1-> dir
        '''
        super(calculate, self).__init__()
        self.image = image
        self.refImage = refImage
        self.resImage = resImage
        self.type = type
    def __del__(self):
        self.wait()

    def run(self):
        if(self.refImage == None):
            self.refImage = ""
        if(self.type==0):
            self.signal.emit(0.5)
            p = registration(flo=self.image,res=self.resImage,ref=self.refImage)
            self.signal.emit(1)
        #batch mode
        else:
            self.signal.emit(0.01)
            images = checkDir(self.image)
            i = 1
            for image in images:
                registration(flo=image,res=os.path.join(self.resImage,"Reg"+os.path.basename(image)),ref=self.refImage)
                self.signal.emit(i/len(images))
                i += 1
            self.signal.emit(1)
    def callback(self, msg):
        # self._signal.emit(msg)
        pass


# this is the previous mode
# ------------------------------------------
# ------------------------------------------
# import nipy
# from nipy.algorithms import registration
# from nipy.algorithms import resample
# import os
# def reg(imagePath,SavePath):
#     image = nipy.load_image(imagePath)
#     target = nipy.load_image(os.path.join(os.getcwd(),'Core',"Ref.nii"))
#
#     similarity = 'crl1'
#     renormalize = False
#     interp = 'pv'
#     optimizer = 'powell'
#     R = registration.HistogramRegistration(image, target, similarity=similarity, interp=interp,
#                               renormalize=renormalize)
#     T = R.optimize('affine', optimizer=optimizer)
#
#     It = registration.resample(image, T.inv(), reference=target)
#     It = resample.resample_img2img(It, target=target)
#     nipy.save_image(It, SavePath)