# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI import mainUI
from Core.RegistrationDis import RegWindow
from Core.BetDis import BetWindow
from Core.BFCDis import BFCwindow
from Core.BrainSegDis import BrinSegwindow
from Core.SegmentDis import Segment
from Core.BatchDis import  Batchwindow
from Core.Dicom2niiDis import  DicomWindow
from Core.FeatureDis import FeatureWindow
from Core.DataDis import DataWindow
#from main_window import MainWindow
#os.environ["PATH"] = os.environ["PATH"]+';'+"E:/Miniconda3/envs/brainTools/MinGW/x86_64-w64-mingw32/bin"
# theano.config.floatX = 'float32'
# theano.config.dtype = 'float32'
# theano.config.gcc.cxxflags = 'E:/Miniconda3/envs/brainTools/MinGW/'
# theano.config.cxx = "E:/Miniconda3/envs/brainTools/MinGWMinGW/x86_64-w64-mingw32/g++.exe"
class MainWindow(QMainWindow, mainUI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

if __name__ == '__main__':
    #freeze_support()
    app = QApplication(sys.argv)
    main = MainWindow()
    dicom = DicomWindow()
    reg = RegWindow()
    ex = FeatureWindow()
    bet = BetWindow()
    seg = Segment()
    bfc = BFCwindow()
    bseg = BrinSegwindow()
    bacth = Batchwindow()
    data = DataWindow()
    # #main = tca_pyqt.MainWin()
    main.show()
    main.BtnFeature.clicked.connect(ex.show)
    main.BtnDicom.clicked.connect(dicom.show)
    main.BtnReg.clicked.connect(reg.show)
    main.BtnSeg.clicked.connect(seg.show)
    main.BtnBet.clicked.connect(bet.show)
    main.BFC.clicked.connect(bfc.show)
    main.BtnBrainSeg.clicked.connect(bseg.show)
    main.BtnBatch.clicked.connect(bacth.show)
    main.BtnReport.clicked.connect(data.show)
    sys.exit(app.exec_())
################################################################################
    #
    # app = QApplication(sys.argv)
    # mainWindow = MainWin(0)
    # mainWindow.show()
    # app.exec_() # 执行
