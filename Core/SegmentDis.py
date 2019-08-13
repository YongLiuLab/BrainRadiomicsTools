# coding=UTF-8
from PyQt5.QtWidgets import QDialog, QFileDialog,QMessageBox  # Qt窗体模块
from Core.hippoSeg.segment import segment
from UI.ui_segment import Ui_Dialog
from PyQt5.QtCore import QThread,pyqtSignal


class Segment(QDialog):
    def __init__(self):
        #初始化界面
        super(Segment, self).__init__()     # 调用父类初始化
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        ''' 信号与槽的连接 '''
        self.ui.input_pushButton.clicked.connect(self.slot_file_input)
        self.ui.output_pushButton.clicked.connect(self.slot_file_output)
        self.ui.run_pushButton.clicked.connect(self.slot_run0)

        self.ui.RadioBtn_File.setChecked(True)
    def slot_file_input(self):      # 输入文件路径
        if(self.ui.RadioBtn_Dir.isChecked()):
            self.filename_input = QFileDialog.getExistingDirectory(self)
        else:
            self.filename_input,filetype = QFileDialog.getOpenFileName(self)
        self.ui.input_lineEdit.setText(self.filename_input)

    def slot_file_output(self):     # 选择输出路径
        self.directory_output = QFileDialog.getExistingDirectory(self)
        self.ui.output_lineEdit.setText(self.directory_output)
        return self.directory_output

    def slot_run0(self):    # 避免UI堵塞，开启新线程
        # self.pb = ProgressBar()     # 进度条显示
        # self.pb.show()
        from Core.utils import checkDir,checkFile
        if self.ui.RadioBtn_Dir.isChecked():
            if len(checkDir(self.filename_input)) == 0:
                QMessageBox.information(self, "Warning", "The directory path is not valid!", QMessageBox.Yes)
                return
        else:
            if checkFile(self.filename_input) == 1:
                QMessageBox.information(self, "Warning", "The image path is not valid!", QMessageBox.Yes)
                return
        self.ui.run_pushButton.setDisabled(True)
        self.thread = RunThread(self.filename_input,self.directory_output,Type=self.ui.RadioBtn_Dir.isChecked())
        self.thread.trigger.connect(self.process)
        self.thread.start()
    def process(self,p):
        if(p==0):
            self.ui.run_pushButton.setDisabled(False)
            QMessageBox.information(self, "Information", "Calculate Done!", QMessageBox.Yes)
        else:
            self.ui.run_pushButton.setDisabled(False)
            QMessageBox.information(self, "Information", "Calculate ERROR!", QMessageBox.Yes)
class RunThread(QThread):
    # python3,pyqt5与之前的版本有些不一样
    #  通过类成员对象定义信号对象
    # _signal = pyqtSignal(str)

    trigger = pyqtSignal(int)

    def __init__(self, filename_input,directory_output ,Type=False,parent=None):
        super(RunThread, self).__init__()
        self.filename_input = filename_input
        self.directory_output = directory_output
        self.Type = Type # True dir method / False Single file
        print(Type)
    def __del__(self):
        self.wait()

    def run(self):
        p = segment(self.filename_input,self.directory_output,self.Type)
        self.trigger.emit(p)

    def callback(self, msg):
        # self._signal.emit(msg)
        pass
