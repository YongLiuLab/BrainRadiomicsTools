from UI import featureUI
from PyQt5.QtWidgets import QWidget,QFileDialog,QMessageBox
from PyQt5.QtCore import QThread,pyqtSignal
from Core import Feature
import numpy
from multiprocessing import Queue
import os
import SimpleITK as sitk
Q = Queue()
class FeatureWindow(QWidget,featureUI.FeatureDialog):
    def __init__(self,parent=None):
        super(FeatureWindow,self).__init__(parent=parent)
        self.initUI()
    def chooseImage(self):
        if self.fileRadiobtn.isChecked():
            self.imageFile, ok = QFileDialog.getOpenFileName(self, "Open File", "../",
                                                             "Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.lineTextImage.setText(self.imageFile)
        else:
            self.directory1 = QFileDialog.getExistingDirectory(self, "Choose DIR", "./")
            self.lineTextImage.setText(self.directory1)

    def chooseMask(self):
        if self.fileRadiobtn.isChecked():
            self.maskFile, ok = QFileDialog.getOpenFileName(self, "Open File", "../",
                                                            "Nii File (*.nii);;Nii.gz (*.nii.gz)")
            self.lineTextMask.setText(self.maskFile)
        else:
            self.directory2 = QFileDialog.getExistingDirectory(self, "Choose DIR", "./")
            self.lineTextMask.setText(self.directory2)

    def outputFile(self):
        self.fileName, ok2 = QFileDialog.getSaveFileName(self,
                                                         "Save File",
                                                         "./",
                                                         "CSV Files (*.csv)")
        self.in3.setText(self.fileName)

    def runCal(self):
        self.pbar.setValue(1)
        if (self.fileRadiobtn.isChecked()):
            self.thread = RunThread(self.imageFile, self.maskFile, self.fileName ,type='singleFile')
        else:
            self.thread = RunThread(self.directory1, self.directory2, self.fileName, type="dir")
        self.thread.start()
        # self.thread2 = procThread()
        # self.thread2.start()
        self.thread.trigger.connect(self.process)
        self.btn4.setText("Calculating...")
        self.btn4.setDisabled(True)

    def process(self, p):
        self.pbar.setValue(p)
        if (p == 100):
            self.btn4.setText("ReStart!")
            self.btn4.setDisabled(False)
            self.show_message()

    def show_message(self):
        QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)

# 多核计算时调用监听线程，负责接受其他进程的消息并返回主线程走进度条
class procThread(QThread):
    signal = pyqtSignal(float)

    def __init__(self):
        super(procThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        # 处理你要做的业务逻辑，这里是通过一个回调来处理数据，这里的逻辑处理写自己的方法
        # wechat.start_auto(self.callback)
        # self._signal.emit(msg);  可以在这里写信号焕发
        while True:
            p = Q.get()
            # 返回p值，即进度值
            self.signal.emit(p)
            if p == 100:
                break
        # self._signal.emit(msg)

    def callback(self, msg):
        # 信号焕发，我是通过我封装类的回调来发起的
        # self._signal.emit(msg)
        pass
    # 计算线程，生成feature计算类 开始计算


class RunThread(QThread):
    trigger = pyqtSignal(float)

    def __init__(self, directory1, directory2, fileName, type="singleFile"):
        super(RunThread, self).__init__()
        self.d1 = directory1
        self.d2 = directory2
        self.type = type
        self.fname = fileName

    def __del__(self):
        self.wait()

    def run(self):
        # 处理你要做的业务逻辑，这里是通过一个回调来处理数据，这里的逻辑处理写自己的方法
        # wechat.start_auto(self.callback)
        # self._signal.emit(msg);  可以在这里写信号焕发
        if ((self.d1 != None or '') and (self.d2 != None or '') and (self.fname != None or '')):
            if self.type == "dir":
                cases = Feature.getFilesDir(self.d1, self.d2)
            else:
                cases = [{"Image": self.d1, "Mask": self.d2, "Subject": os.path.basename(self.d1),
                          "Patient": os.path.basename(self.d2)}]
            settings = {}
            settings['binWidth'] = 25
            settings['label'] = 1
            settings[
                'resampledPixelSpacing'] = None  # [3,3,3] is an example for defining resampling (voxels with size 3x3x3mm)
            settings['interpolator'] = sitk.sitkBSpline
            settings['sigma'] = numpy.arange(5., 0., -.5)[::1]
            # 确保simpleITK加载文件时只使用一个线程，避免多线程出错
            sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(1)
            feature = Feature.feature(cases=cases, settings=settings, outputfile=self.fname,
                                      notDisplayType=Feature.notDisplayType)
            feature.singleRun()
            self.trigger.emit(100)

    def callback(self, msg):
        # self._signal.emit(msg)
        pass
