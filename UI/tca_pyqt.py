#coding=utf-8

import nibabel as ni
import numpy as np
# from nilearn.image import smooth_img
import os,sys
import scipy.io as scio
# import pandas as pd
# import PyQt5
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, QLineEdit, QGridLayout, QApplication, QAction, qApp, QToolTip, QSpinBox, QComboBox,QPushButton
# from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, pyqtSignal,QRect
from PyQt5.QtGui import QFont, QIcon
from display import *

################################################################################

################################################################################

class MainWin(QMainWindow):
    size_x = 800
    size_y = 650
    sizeChanged = pyqtSignal()

    def __init__(self, lan = 0, parent=None):
        super(MainWin, self).__init__(parent=parent)
        self.lan = lan # 设置语言
        self.initUI()
        self.sizeChanged.connect(self.adjustSize)

    def initUI(self):
        self.display_min = 0 # 图像显示最大值(对应灰度值为255)
        self.display_max = 1 # 图像显示最小值(对应灰度值为0)
        self.display_x = 0 # 显示图像的x坐标
        self.display_y = 0 # 显示图像的y坐标
        self.display_z = 0 # 显示图像的z坐标
        self.display_vol = -1 # 显示图像的volume序列
        self.ratio = [1, 1, 1.25] # 显示图像的比例

        self.fname = "" # 显示图像的路径
        self.nii = "" # 对应图像的nii
        self.nii_display = "" # 显示用的nii数据(值转换为对应的0-255)
        self.pixmap_a = ""
        self.pixmap_c = ""
        self.pixmap_s = "" # 用于在子窗口显示的单幅图像*3

        #显示图像的label
        self.label_axial = QLabel("NMD!WSM?", self)
        self.label_axial.setStyleSheet("border: 1px solid black") # 设置label边框
        self.label_axial.setScaledContents(True) # 设置图像自适应修改大小
        self.label_axial.setMouseTracking(False) # 设置鼠标点击任意键时才捕捉鼠标位置
        self.label_axial.mousePressEvent = self.click_a # 鼠标点击时修改显示的另两个视图位置
        self.label_axial.mouseMoveEvent = self.click_a # 鼠标拖拽时修改显示的另两个试图位置
        self.label_axial.mouseDoubleClickEvent = self.double_click_a # 鼠标进行双击时显示对应slice的图像

        self.label_coronal = QLabel("NMD!WSM?", self) # 同上
        self.label_coronal.setStyleSheet("border: 1px solid black")
        self.label_coronal.setScaledContents(True)
        self.label_coronal.setMouseTracking(False)
        self.label_coronal.mousePressEvent = self.click_c
        self.label_coronal.mouseMoveEvent = self.click_c
        self.label_coronal.mouseDoubleClickEvent = self.double_click_c

        self.label_sagittal = QLabel("NMD!WSM?", self) # 同上
        self.label_sagittal.setStyleSheet("border: 1px solid black")
        self.label_sagittal.setScaledContents(True)
        self.label_sagittal.setMouseTracking(False)
        self.label_sagittal.mousePressEvent = self.click_s
        self.label_sagittal.mouseMoveEvent = self.click_s
        self.label_sagittal.mouseDoubleClickEvent = self.double_click_s

        # 显示图像信息的框架
        self.grid_info = QGridLayout() # 设置信息总框架
        # 显示图像文件路径
        if self.lan == 0:
            self.label_name_dir = QLabel("Directory:", self) # 设置显示文件路径信息条目的label
        elif self.lan == 1:
            self.label_name_dir = QLabel("文件路径:", self)
        self.label_val_dir = QLineEdit(self) # 设置显示文件路径具体信息的label
        self.label_val_dir.setText(self.fname)
        # 显示图像数据类型
        if self.lan == 0:
            self.label_name_datype = QLabel("Data Type:", self)
        elif self.lan == 1:
            self.label_name_datype = QLabel("数据类型:", self)
        self.label_val_datype = QLineEdit(self)
        self.label_val_datype.setEnabled(False) # 设置图像数据格式为不可修改
        try:
            self.label_val_datype.setText(str(self.nii.header.get("datatype").dtype))
        except AttributeError:
            pass

        # 显示图像维度信息
        if self.lan == 0:
            self.label_name_diminfo = QLabel("Dim:", self)
        elif self.lan == 1:
            self.label_name_diminfo = QLabel("图像维度:", self)
        self.label_val_diminfo = QLineEdit(self)
        self.label_val_diminfo.setEnabled(False) # 设置图像维度信息为不可修改
        try:
            self.label_val_diminfo.setText(str(self.nii.get_data().shape))
        except AttributeError:
            pass

        if self.lan == 0:
            self.label_name_resinfo = QLabel("Resolution", self)
        elif self.lan == 1:
            self.label_name_resinfo = QLabel("分辨率:", self)
        self.label_val_resinfo = QLineEdit(self)
        self.label_val_resinfo.setEnabled(False) # 设置图像分辨率信息为不可修改
        try:
            self.label_val_resinfo.setText("(" + str((self.nii.header.get("pixdim"))[1])+", "+str((self.nii.header.get("pixdim"))[2])+", "+str((self.nii.header.get("pixdim"))[3])+", "+str((self.nii.header.get("pixdim"))[0])+")")
        except AttributeError:
            pass

        # 显示图像显示比例
        if self.lan == 0:
            self.label_name_disratio = QLabel("Display Ratio:", self)
        elif self.lan == 1:
            self.label_name_disratio = QLabel("显示比例:", self)
        self.grid_val_disratio = QGridLayout()
        self.label_ratio_1 = QLineEdit(self)
        self.label_ratio_2 = QLineEdit(self)
        self.label_ratio_3 = QLineEdit(self)
        if self.lan == 0:
            self.but_ratio = QPushButton("RESET", self)
        elif self.lan == 1:
            self.but_ratio = QPushButton("重置", self)
        self.label_ratio_1.setText(str(self.ratio[0]))
        self.label_ratio_2.setText(str(self.ratio[1]))
        self.label_ratio_3.setText(str(self.ratio[2]))
        self.label_ratio_1.editingFinished.connect(self.modify_ratio_1) # 修改显示比例后，调节显示比例
        self.label_ratio_2.editingFinished.connect(self.modify_ratio_2)
        self.label_ratio_3.editingFinished.connect(self.modify_ratio_3)
        self.but_ratio.clicked.connect(self.reset_ratio) # 重置显示比例为默认值

        # 显示图像对应slice
        if self.lan == 0:
            self.label_name_disvol = QLabel("Display volume:", self)
        elif self.lan == 1:
            self.label_name_disvol = QLabel("显示位置:", self)
        self.grid_val_disvol = QGridLayout()
        self.spin_x = QSpinBox(self)
        self.spin_y = QSpinBox(self)
        self.spin_z = QSpinBox(self)
        # self.combox_x = QLineEdit(self)
        # self.combox_y = QLineEdit(self)
        # self.combox_z = QLineEdit(self)
        self.combox_t = QComboBox(self)
        self.combox_t.activated.connect(self.switch_vol) # 点击下拉菜单切换显示的volume
        # self.combox_x.editingFinished.connect(self.modify_slice_x) # 通过在文本框中输入坐标来完成显示切换
        # self.combox_y.editingFinished.connect(self.modify_slice_y)
        # self.combox_z.editingFinished.connect(self.modify_slice_z)
        self.spin_x.valueChanged.connect(self.modify_slice_x)
        self.spin_y.valueChanged.connect(self.modify_slice_y)
        self.spin_z.valueChanged.connect(self.modify_slice_z)
        self.spin_x.setWrapping(True)
        self.spin_y.setWrapping(True)
        self.spin_z.setWrapping(True)
        self.spin_x.setMinimum(1)
        self.spin_y.setMinimum(1)
        self.spin_z.setMinimum(1)
        self.spin_x.setMaximum(1)
        self.spin_y.setMaximum(1)
        self.spin_z.setMaximum(1)

        # 显示图像显示范围
        if self.lan == 0:
            self.label_name_disrange = QLabel("Display range:", self)
        elif self.lan == 1:
            self.label_name_disrange = QLabel("显示范围:", self)
        self.grid_val_disrange = QGridLayout()
        self.label_val_min = QLineEdit(self)
        self.label_val_max = QLineEdit(self)
        if self.lan == 0:
            self.but_range = QPushButton("RESET", self)
        elif self.lan == 1:
            self.but_range = QPushButton("重置", self)
        self.label_val_min.editingFinished.connect(self.modify_min) # 修改显示范围后，对应修改显示范围
        self.label_val_max.editingFinished.connect(self.modify_max)
        self.but_range.clicked.connect(self.reset_range) # 重置显示范围为默认值

        # 安排组件位置
        self.grid_val_disratio.addWidget(self.label_ratio_1, 0, 0)
        self.grid_val_disratio.addWidget(self.label_ratio_2, 0, 1)
        self.grid_val_disratio.addWidget(self.label_ratio_3, 0, 2)
        self.grid_val_disratio.addWidget(self.but_ratio, 0, 3)

        # self.grid_val_disvol.addWidget(self.combox_x, 0, 1)
        # self.grid_val_disvol.addWidget(self.combox_y, 0, 2)
        # self.grid_val_disvol.addWidget(self.combox_z, 0, 3)
        self.grid_val_disvol.addWidget(self.spin_x, 0, 1)
        self.grid_val_disvol.addWidget(self.spin_y, 0, 2)
        self.grid_val_disvol.addWidget(self.spin_z, 0, 3)
        self.grid_val_disvol.addWidget(self.combox_t, 0, 0)

        self.grid_val_disrange.addWidget(self.label_val_min, 0, 0)
        self.grid_val_disrange.addWidget(self.label_val_max, 0, 1)
        self.grid_val_disrange.addWidget(self.but_range, 0, 2)

        self.grid_info.addWidget(self.label_name_dir, 0, 0)
        self.grid_info.addWidget(self.label_val_dir, 0, 1)
        self.grid_info.addWidget(self.label_name_datype, 1, 0)
        self.grid_info.addWidget(self.label_val_datype, 1, 1)
        self.grid_info.addWidget(self.label_name_diminfo, 2, 0)
        self.grid_info.addWidget(self.label_val_diminfo, 2, 1)
        self.grid_info.addWidget(self.label_name_resinfo, 3, 0)
        self.grid_info.addWidget(self.label_val_resinfo, 3, 1)
        self.grid_info.addWidget(self.label_name_disratio, 4, 0)
        self.grid_info.addLayout(self.grid_val_disratio, 4, 1)
        self.grid_info.addWidget(self.label_name_disvol, 5, 0)
        self.grid_info.addLayout(self.grid_val_disvol, 5, 1)
        self.grid_info.addWidget(self.label_name_disrange, 6, 0)
        self.grid_info.addLayout(self.grid_val_disrange, 6, 1)

        # 设置菜单
        if self.lan == 0:
            openAction = QAction('&Open Nii File...', self) # 将对应功能加入菜单栏对应子项中
            openAction.setStatusTip('Select and open a Nifti file')
        elif self.lan == 1:
            openAction = QAction('打开nii文件...', self) # 将对应功能加入菜单栏对应子项中
            openAction.setStatusTip('选择并打开一个Nifti格式文件')
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.OpenFile)

        if self.lan == 0:
            saveAction = QAction('&Save...', self)
            saveAction.setStatusTip('Save current nii file in display')
        elif self.lan == 1:
            saveAction = QAction('保存文件...', self)
            saveAction.setStatusTip('将正在显示的图像保存为nii文件')
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.SaveFile)

        if self.lan == 0:
            exitAction = QAction('&Quit', self)
            exitAction.setStatusTip('Exit')
        elif self.lan == 1:
            exitAction = QAction('退出', self)
            exitAction.setStatusTip('退出程序')
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        if self.lan == 0:
            SegmentAction = QAction('&Segment', self)
            SegmentAction.setStatusTip('Segment image into grey matter, white matter and csf')
        elif self.lan == 1:
            SegmentAction = QAction('分割', self)
            SegmentAction.setStatusTip('将图像分割为灰质、白质、脑脊液三部分')
        SegmentAction.setShortcut('Ctrl+E')
        SegmentAction.triggered.connect(qApp.quit)

        if self.lan == 0:
            CoregisterAction = QAction('&Coregister', self)
            CoregisterAction.setStatusTip('Coregister target image with reference image')
        elif self.lan == 1:
            CoregisterAction = QAction('配准', self)
            CoregisterAction.setStatusTip('将目标图像与参考图像进行配准')
        CoregisterAction.setShortcut('Ctrl+C')
        CoregisterAction.triggered.connect(qApp.quit)

        if self.lan == 0:
            CalcbfAction = QAction('&Calculate CBF from ASL', self)
            CalcbfAction.setStatusTip('Calculate CBF image from different ASL images or DWI image')
        elif self.lan == 1:
            CalcbfAction = QAction('通过ASL计算CBF', self)
            CalcbfAction.setStatusTip('通过不同时间的ASL像或DWI像计算CBF图像')
        CalcbfAction.setShortcut('Ctrl+A')
        CalcbfAction.triggered.connect(self.CalculateCbf)

        if self.lan == 0:
            PVEAction = QAction('&Partial Volume Correlation', self)
            PVEAction.setStatusTip('Operate Partial Volume Correlation for CBF image')
        elif self.lan == 1:
            PVEAction = QAction('局部空间校正', self)
            PVEAction.setStatusTip('对CBF图像进行局部空间校正')
        PVEAction.setShortcut('Ctrl+P')
        PVEAction.triggered.connect(self.PVECbf)


        QToolTip.setFont(QFont('SansSerif', 10)) # 没用的字体
        self.setGeometry(250, 100, 800, 650) # 修改窗口大小
        self.setWindowTitle('Toolkit_Test') #修改程序显示标题
        self.setWindowIcon(QIcon('source/images.jpg')) # 修改程序显示图标
        self.setMinimumSize(300,300) # 设置允许修改到的最小窗口大小

        # 显示状态栏，可用于显示菜单栏的备注
        self.statusBar()

        menubar = self.menuBar()
        if self.lan == 0:
            fileMenu = menubar.addMenu('&File') # 为菜单栏增加子项
        elif self.lan == 1:
            fileMenu = menubar.addMenu('文件')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        if self.lan == 0:
            dispMenu = menubar.addMenu('&Display')
        elif self.lan == 1:
            dispMenu = menubar.addMenu('显示')

        if self.lan == 0:
            cbfMenu = menubar.addMenu('&Preprocess')
        elif self.lan == 1:
            cbfMenu = menubar.addMenu('预处理')
        cbfMenu.addAction(SegmentAction)
        cbfMenu.addAction(CoregisterAction)

        if self.lan == 0:
            calMenu = menubar.addMenu('&Calculation')
        elif self.lan == 1:
            calMenu = menubar.addMenu('计算')
        calMenu.addAction(CalcbfAction)
        calMenu.addAction(PVEAction)

    def modify_min(self):
    # 调整图像的最小显示值
        try:
            temp = float(self.label_val_min.text())
            self.display_min = temp
            if self.display_min > self.display_max:
                self.display_min, self.display_max = self.display_max, self.display_min
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        except ValueError:
            pass

    def modify_max(self):
    # 调整图像的最大显示值
        try:
            temp = float(self.label_val_max.text())
            self.display_max = temp
            if self.display_min > self.display_max:
                self.display_min, self.display_max = self.display_max, self.display_min
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        except ValueError:
            pass

    def reset_range(self):
    # 重置显示范围
        try:
            temp_data = self.nii.get_data()
            if len(temp_data.shape) == 4:
                self.display_min, self.display_max = np.percentile(temp_data[:,:,:,self.display_vol],[2.5,97.5])
            elif len(temp_data.shape) == 3:
                self.display_min, self.display_max = np.percentile(temp_data,[2.5,97.5])
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
            self.refreshInfo()
        except AttributeError:
            pass

    def switch_vol(self, text):
    # 切换显示volume(一般为不同时间序列，也可能为不同模态图像)
        self.display_vol = int(text)
        self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
        self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        self.reset_range()
        self.refreshInfo()

    def refreshInfo(self):
    # 更新图像信息
        self.label_val_dir.setText(self.fname)
        try:
            self.label_val_datype.setText(str(self.nii.header.get("datatype").dtype))
            self.label_val_diminfo.setText(str(self.nii.get_data().shape))
            self.label_val_resinfo.setText("(" + str((self.nii.header.get("pixdim"))[1])+", "+str((self.nii.header.get("pixdim"))[2])+", "+str((self.nii.header.get("pixdim"))[3])+", "+str((self.nii.header.get("pixdim"))[0])+")")
            # self.combox_x.setText(str(self.display_x + 1))
            # self.combox_y.setText(str(self.display_y + 1))
            # self.combox_z.setText(str(self.display_z + 1))
            self.spin_x.setValue(self.display_x + 1)
            self.spin_y.setValue(self.display_y + 1)
            self.spin_z.setValue(self.display_z + 1)
            self.label_val_min.setText(str(self.display_min))
            self.label_val_max.setText(str(self.display_max))
            try:
                value = self.nii.get_data()[-1-self.display_x, self.display_y, -1-self.display_z]
                self.statusBar().showMessage("("+str(self.display_x+1)+","+str(self.display_y+1)+","+str(self.display_z+1)+"):"+str(value))
            except IndexError:
                try:
                    value = self.nii.get_data()[-1-self.display_x, self.display_y, -1-self.display_z]
                    self.statusBar().showMessage("("+str(self.display_x+1)+","+str(self.display_y+1)+","+str(self.display_z+1)+"):"+str(value))
                except IndexError:
                    pass
        except AttributeError:
            pass

    def modify_slice_x(self):
    # 修改显示的x轴坐标
        try:
            x_max = self.nii.shape[0]
            # temp = int(self.combox_x.text()) - 1
            temp = self.spin_x.value() - 1
            if temp + 1 <= x_max and temp >= 0:
                self.display_x = temp
            else:
                warn_msg(self, "Out of range!")
                if temp < 0:
                    self.display_x = 0
                else:
                    self.display_x = x_max - 1
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        except AttributeError:
            pass
        except IndexError:
            pass
        self.adjustSize()

    def modify_slice_y(self):
    # 修改显示的y轴坐标
        try:
            y_max = self.nii.shape[1]
            # temp = int(self.combox_y.text()) - 1
            temp = self.spin_y.value() - 1
            if temp + 1 <= y_max and temp >= 0:
                self.display_y = temp
            else:
                warn_msg(self, "Out of range!")
                if temp < 0:
                    self.display_y = 0
                else:
                    self.display_y = y_max - 1
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        except AttributeError:
            pass
        except IndexError:
            pass
        self.adjustSize()

    def modify_slice_z(self):
    # 修改显示的z轴坐标
        try:
            z_max = self.nii.shape[2]
            # temp = int(self.combox_z.text()) - 1
            temp = self.spin_z.value() - 1
            if temp + 1 <= z_max and temp >= 0:
                self.display_z = temp
            else:
                warn_msg(self, "Out of range!")
                if temp < 0:
                    self.display_z = 0
                else:
                    self.display_z = z_max - 1
            self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
            self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
        except AttributeError:
            pass
        except IndexError:
            pass
        self.adjustSize()

    def modify_ratio_1(self):
    # 修改显示比例，与modify_ratio_2, modify_ratio_3结合使用
        temp = self.label_ratio_1.text()
        if temp > "0" and temp <= "9":
            try:
                self.ratio[0] = float(self.label_ratio_1.text())
            except ValueError:
                warn_msg(self, "Invalid Input.")
        else:
            # print(temp)
            warn_msg(self, "The value should be in the range between 0 and 9.")
        self.adjustSize()

    def modify_ratio_2(self):
        temp = self.label_ratio_2.text()
        if temp > "0" and temp <= "9":
            try:
                self.ratio[1] = float(self.label_ratio_2.text())
            except ValueError:
                warn_msg(self, "Invalid Input.")
        else:
            # print(temp)
            warn_msg(self, "The value should be in the range between 0 and 9.")
        self.adjustSize()

    def modify_ratio_3(self):
        temp = self.label_ratio_3.text()
        if temp > "0" and temp <= "9":
            try:
                self.ratio[2] = float(self.label_ratio_3.text())
            except ValueError:
                warn_msg(self, "Invalid Input.")
        else:
            # print(temp)
            warn_msg(self, "The value should be in the range between 0 and 9.")
        self.adjustSize()

    def reset_ratio(self):
    # 将显示比例重置为默认值
        self.ratio = [1,1,1.25]
        self.label_ratio_1.setText(str(self.ratio[0]))
        self.label_ratio_2.setText(str(self.ratio[1]))
        self.label_ratio_3.setText(str(self.ratio[2]))
        self.adjustSize()

    def double_click_a(self, event):
    # 双击Axial视图，可以将正在显示的slice在子窗口中打开并进行后续操作
        if self.nii != "":
            if self.lan == 0:
                sub_window = subWindow(0, "DISPLAY AXIAL", self.lan, self)
            elif self.lan == 1:
                sub_window = subWindow(0, "显示轴向切片", self.lan, self)
            else:
                sub_window = subWindow(0, "+----+", self.lan, self)

            sub_window.show()

    def double_click_c(self, event):
    # 双击Coranal视图，可以将正在显示的slice在子窗口中打开并进行后续操作
        if self.nii != "":
            if self.lan == 0:
                sub_window = subWindow(1, "DISPLAY CORONAL", self.lan, self)
            elif self.lan == 1:
                sub_window = subWindow(1, "显示冠状切片", self.lan, self)
            else:
                sub_window = subWindow(1, "+----+", self.lan, self)

            sub_window.show()

    def double_click_s(self, event):
    # 双击Sagittal视图，可以将正在显示的slice在子窗口中打开并进行后续操作
        if self.nii != "":
            if self.lan == 0:
                sub_window = subWindow(2, "DISPLAY SAGITTAL", self.lan, self)
            elif self.lan == 1:
                sub_window = subWindow(2, "显示矢状切片", self.lan, self)
            else:
                sub_window = subWindow(2, "+----+", self.lan, self)

            sub_window.show()

    def click_a(self, event):
    # 单击/拖拽Axial视图，调整其它视图到单击对应的点, 右键点击显示对应点数值
        if self.nii != "":
            x, z = event.pos().x(), event.pos().y() # 捕捉操作点
            # print(event.pos())
            ratio_1 = self.ratio[1] / self.ratio[0]
            ratio_2 = self.ratio[2] / self.ratio[0]
            temp_size = min((self.width() - 150) / (1 + ratio_2), (self.height() - 150) / (ratio_1 + ratio_2))
            height = temp_size * ratio_1
            width = temp_size
            # print(width, height)
            self.display_x = int(x / width * self.nii.shape[0])
            self.display_z = int(z / height * self.nii.shape[2])# 计算操作点对应的数据位置
            # print(self.display_x, self.display_z)
            # print(self.nii.shape)
            self.refreshInfo()
            try:
                self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)
                self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
            except IndexError: # 防止超出显示范围
                pass



    def click_c(self, event):
    # 单击/拖拽Coronal视图，调整其它视图到单击对应的点
        if self.nii != "":
            y, z = event.pos().x(), event.pos().y()
            ratio_1 = self.ratio[1] / self.ratio[0]
            ratio_2 = self.ratio[2] / self.ratio[0]
            temp_size = min((self.width() - 150) / (1 + ratio_2), (self.height() - 150) / (ratio_1 + ratio_2))
            height = temp_size * ratio_1
            width = temp_size * ratio_2
            self.display_y = int(y / width * self.nii.shape[1])
            self.display_z = int(z / height * self.nii.shape[2])
            self.refreshInfo()
            try:
                self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)

                self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
            except IndexError:
                pass

    def click_s(self, event):
    # 单击/拖拽Sagittal视图，调整其它视图到单击对应的点
        if self.nii != "":
            x, y = event.pos().x(), event.pos().y()
            ratio_1 = self.ratio[1] / self.ratio[0]
            ratio_2 = self.ratio[2] / self.ratio[0]
            temp_size = min((self.width() - 150) / (1 + ratio_2), (self.height() - 150) / (ratio_1 + ratio_2))
            height = temp_size * ratio_2
            width = temp_size
            self.display_y = int((height - y) / height * self.nii.shape[1])
            self.display_x = int((x) / width * self.nii.shape[0])
            self.refreshInfo()
            try:
                self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)

                self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
            except IndexError:
                pass


    def resizeEvent(self, event):
    # 捕捉调节窗口大小的动作(可简化)
        self.sizeChanged.emit()
        return super(MainWin, self).resizeEvent(event)

    def adjustSize(self):
    # 将组件的位置大小调节成与窗口实际大小相适应
        ratio_1 = self.ratio[1] / self.ratio[0]
        ratio_2 = self.ratio[2] / self.ratio[0]
        temp_size = min((self.width() - 150) / (1 + ratio_2), (self.height() - 150) / (ratio_1 + ratio_2)) # 只考虑实际计算过程中会产生的最短边
        self.label_axial.setGeometry(50, 50, int(temp_size), int(temp_size * ratio_1))
        self.label_coronal.setGeometry(int(temp_size + 100), 50 ,int(temp_size * ratio_2), int(temp_size * ratio_1))
        self.label_sagittal.setGeometry(50, int(temp_size * ratio_1 + 100), int(temp_size), int(temp_size * ratio_2))
        self.grid_info.setGeometry(QRect(int(temp_size + 100), int(temp_size * ratio_1 + 100), int(temp_size * ratio_2), int(temp_size * ratio_2)))
        self.refreshInfo()

    def OpenFile(self):
    # 打开文件，只能打开nii或nii.gz后缀的文件，否则无法读取
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', './', "Nii Files (*.nii;*.nii.gz);;All Files (*)")[0]
        # self.nii = ni.load(fname)
        if self.fname == "":
            print("I'm not done yet.")
        else:
            try:
                self.nii = ni.load(self.fname)
                self.display_vol = -1
                temp_data = self.nii.get_data()

                self.spin_x.setMaximum(temp_data.shape[0])
                self.spin_y.setMaximum(temp_data.shape[1])
                self.spin_z.setMaximum(temp_data.shape[2])

                if len(temp_data.shape) == 4:
                    self.display_min, self.display_max = np.percentile(temp_data[:,:,:,0],[2.5,97.5])
                elif len(temp_data.shape) == 3:
                    self.display_min, self.display_max = np.percentile(temp_data,[2.5,97.5]) # 以图像数据分布的前2.5%和后2.5%的体素的数值作为显示时使用的最大/最小值

                self.display_x = int(self.nii.affine[0,3] / ni.load(self.fname).affine[0,0]) + ni.load(self.fname).shape[0]
                self.display_y = int(self.nii.affine[1,3] / ni.load(self.fname).affine[1,1]) + ni.load(self.fname).shape[1]
                self.display_z = int(self.nii.affine[2,3] / ni.load(self.fname).affine[2,2]) + ni.load(self.fname).shape[2] # 通过affine信息计算起始坐标

                self.nii_display = nii2display(self,self.display_vol,self.nii.get_data(), self.display_min, self.display_max)

                self.pixmap_a, self.pixmap_c, self.pixmap_s = display_nii(self, self.nii_display, self.display_x, self.display_y, self.display_z, self.display_vol, self.display_min, self.display_max, self.label_axial, self.label_coronal, self.label_sagittal, self.lan)
                self.display_vol = 0
                temp_t = []
                if len(temp_data.shape) == 4:
                    for i in range(int(temp_data.shape[3])):
                        temp_t.append(str(i + 1))
                self.combox_t.addItems(temp_t) # 设置显示volume对应的下拉菜单
                self.refreshInfo()
            except FileNotFoundError:
                warn_msg(self, "File not existed.")
                self.fname == "" # 防止输入不存在的路径
            except ni.filebasedimages.ImageFileError:
                warn_msg(self, "Not an nii file.")
                self.fname == "" # 防止输入的路径不是nii文件

    def SaveFile(self):
    # 保存文件，只能保存为nii格式
        temp = QFileDialog.getSaveFileName(self, 'Save File As', './', "Nii Files (*.nii);;All Files (*)")
        if temp[0] == "" or self.nii == "":
            print("I'm not done yet.")
        else:
            ni.save(self.nii, temp[0])
            # print(temp)

    def CalculateCbf(self):
        # self.ui_window = ui_cbf(self, self.lan)
        # self.ui_window.show()
        pass

    def PVECbf(self):
        pass
        # self.ui_window = ui_pve(self, self.lan)
        # self.ui_window.show()

    def set_nii(self, nii_done):
        self.nii = nii_done

################################################################################

app = QApplication(sys.argv)
mainWindow = MainWin(0)
mainWindow.show()
app.exec_() # 执行
