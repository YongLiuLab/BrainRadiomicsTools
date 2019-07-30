from PyQt5.QtCore import QThread, pyqtSignal
from Core.hippoSeg import segment
from Core.registration import registration
from Core.setting import batchTempDir
from Core.N4Correct import N4correctWin,N4correct
from Core.bet import Bet
from Core import Feature
from Core.utils import cleanImage
import SimpleITK as sitk
import numpy as np
import os
import time
import csv
import shutil
class batchCal(QThread):
    '''
    qthread 计算线程
    使用各模块的计算函数进行计算
    '''
    signal = pyqtSignal(int)
    strSignal = pyqtSignal(str)
    fileSignal = pyqtSignal(int)
    def __init__(self,dir,images,outputPath,isReg=True,isN4=True,isBet=True,isHs=True,isBs=True,isFeature=True,isData=True):
        super(batchCal, self).__init__()
        self.dir = dir
        self.isReg = isReg
        self.isN4 = isN4
        self.isBet = isBet
        self.isHs = isHs
        self.isBs = isBs
        self.isFeature = isFeature
        self.isData = isData
        self.images = images
        self.outputPath =outputPath
        self.fileIndex = 0
        if(not os.path.exists(batchTempDir)):
            os.mkdir(batchTempDir)
        self.tempDir = os.path.join(batchTempDir,time.strftime("%Y%m%d%H%M", time.localtime()))
        # 进度标志位 完成一项任务 +1
        self.progress = 0

        if(not os.path.exists(self.tempDir)):
            os.mkdir(self.tempDir)
    def calReg(self,path):
        self.strSignal.emit("Image Registration ...")
        regTemp = os.path.realpath(os.path.join(self.tempDir,"_regtemp"))
        if(not os.path.exists(regTemp)):
            os.mkdir(regTemp)

        registration(path,os.path.join(regTemp,os.path.basename(path)),onlyRigid = True)

        self.progress += 1
        self.signal.emit(self.progress)

        return os.path.join(regTemp,os.path.basename(path))
    #only n4 not normalise
    def calN4(self,path):
        self.strSignal.emit("Image N4 bias Correction ...")
        n4Temp = os.path.join(self.tempDir,"_n4temp")
        if(not os.path.exists(n4Temp)):
            os.mkdir(n4Temp)
        outPath = os.path.join(n4Temp,os.path.basename(path))

        N4correctWin(path, outPath, isNorm=False, isBFC=True)

        self.progress += 1
        self.signal.emit(self.progress)
        print(outPath)
        return outPath

    def calBet(self,path):
        self.strSignal.emit("Image Brain Extraction ...")
        betTemp = os.path.join(self.tempDir, "_bettemp")
        if (not os.path.exists(betTemp)):
            os.mkdir(betTemp)
        outPath = os.path.join(betTemp, os.path.basename(path))
        outPath = os.path.realpath(outPath)
        self.progress += 1
        self.signal.emit(self.progress)
        print(outPath)

        #Bet.BrainExtract(path, outPath)
        Bet.BrainExtractFast(path,outPath)
        self.progress += 1
        self.signal.emit(self.progress)
        # bet 默认输出gz ，无法修改
        outPath = outPath+".gz"
        return outPath

    def calHs(self,path):
        self.strSignal.emit("Image Hippocampus Segmentation ...")
        hsTemp = os.path.join(self.tempDir, "_hstemp")
        if (not os.path.exists(hsTemp)):
            os.mkdir(hsTemp)
        outPath = hsTemp
        segment(path,outPath,Type=False)
        # outputpath = seg... + 原文件名
        outFilePath = os.path.join(outPath,"Segmentation_"+os.path.basename(path))
        cleanImagePath = os.path.join(outPath,"Hippo_"+os.path.basename(path))
        cleanImage(outFilePath,cleanImagePath)
        self.progress += 1
        self.signal.emit(self.progress)
        return cleanImagePath
    def calBs(self,path):
        from Core.brainSeg import runSeg
        self.strSignal.emit("Image Brain Segmentation ...")
        bsTemp = os.path.join(self.tempDir, "_bstemp")
        if (not os.path.exists(bsTemp)):
            os.mkdir(bsTemp)
        outPath = bsTemp
        WmLabelPath, GMLabelPath, CsfLabelPath = runSeg.runSeg(path, outPath)

        self.progress += 1
        self.signal.emit(self.progress)
        return WmLabelPath,GMLabelPath,CsfLabelPath
    def calFeature(self,imagePath,labelPath):
        from utils import cleanImage
        self.strSignal.emit("Image Feature Extraction ...")
        featureTemp = os.path.join(self.tempDir, "_featuretemp")
        self.featureTemp = featureTemp
        if (not os.path.exists(featureTemp)):
            os.mkdir(featureTemp)
        outPath = featureTemp
        print("origin image Path",imagePath)
        #LabelCleanPath = os.path.join(outPath,os.path.basename(imagePath))
        #cleanImage(labelPath,LabelCleanPath)
        outCsvPath = os.path.join(outPath,os.path.basename(imagePath)+".csv")
        print("output Csv Path", outCsvPath)
        cases = [{"Image": imagePath, "Mask": labelPath, "Subject": os.path.basename(imagePath),
                      "Patient": os.path.basename(imagePath)}]
        settings = {}
        settings['binWidth'] = 25
        settings['label'] = 1
        settings[
            'resampledPixelSpacing'] = None  # [3,3,3] is an example for defining resampling (voxels with size 3x3x3mm)
        settings['interpolator'] = sitk.sitkBSpline
        settings['sigma'] = np.arange(5., 0., -.5)[::1]
        feature = Feature.feature(cases=cases, settings=settings, outputfile=outCsvPath,
                                  notDisplayType=Feature.notDisplayType)
        # 这里执行单进程即可
        feature.singleRun()

        self.progress += 1
        self.signal.emit(self.progress)
        return outCsvPath
    def csvMerg(self):
        csvs = os.listdir(self.featureTemp)
        csvList = []
        for c in csvs:
            if os.path.basename(c).split(".")[-1] == 'csv':
                csvList.append(c)
        res = []
        for c in csvList:
            with open(os.path.join(self.featureTemp,c),'r') as f:
                reader = csv.DictReader(f)
                c_data = [row for row in reader][0]
                res.append(c_data)

        with open(os.path.join(self.featureTemp,"result.csv"), mode='w') as outputFile:
            writer = csv.DictWriter(outputFile,
                                    fieldnames=list(res[0].keys()),
                                    restval='',
                                    extrasaction='raise',
                                    lineterminator='\n')
            writer.writeheader()
            writer.writerows(res)
    def calData(self,featurePath,wmPath,gmPath,csfPath,hippoPath,originImagePath):
        from Core.Report import reportBuild
        self.dataTemp = os.path.realpath(os.path.join(self.tempDir, "_datatemp"))
        if (not os.path.exists(self.dataTemp)):
            os.mkdir(self.dataTemp)

        reportBuild(featurePath,wmPath,gmPath,csfPath,hippoPath,originImagePath,tempDir=self.dataTemp)

    def plotImage(self):
        pass
    def run(self):
        try:
            for image in self.images:
                self.signal.emit(0)
                self.progress = 0
                image_path = os.path.realpath(os.path.join(self.dir,image))
                baseImagePath = image_path

                # reg -> n4 -> bet
                if(self.isReg):
                    image_path = self.calReg(image_path)
                    baseImagePath = image_path
                if (self.isN4):
                    image_path = self.calN4(image_path)
                if(self.isBet):
                    image_path = self.calBet(image_path)



                if(self.isHs):
                    HippoLabelPath = self.calHs(image_path)
                if(self.isBs):
                    WmLabelPath,GMLabelPath,CsfLabelPath = self.calBs(image_path)
                if(self.isFeature):
                    featurePath  = self.calFeature(image_path,HippoLabelPath)
                if(self.isData):
                    dataPath = self.calData(featurePath,WmLabelPath,GMLabelPath,CsfLabelPath,HippoLabelPath,baseImagePath)
                self.fileSignal.emit(self.fileIndex)
                self.fileIndex += 1
                print("结束循环！")
            if (self.isFeature):
                self.csvMerg()
        except Exception:
            self.signal.emit(-1)
            return
        self.signal.emit(100)

        shutil.copytree(self.tempDir, self.outputPath)
        shutil.rmtree(self.tempDir, True)
        print("dir " + str(self.tempDir) + " removed!")