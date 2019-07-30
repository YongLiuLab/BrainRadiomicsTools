from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm, Inches, Pt
import pandas as pd
from nilearn import plotting
import numpy as np
import csv
import nibabel as nib
import os

reference = {
                "SurfaceArea":[3728.80,4267.30],
                "AreaVolume":[0.610,0.689],
                "Median":[1.58,1.75],
                "Mean":[1.59,1.75],
                "wmVolume":[550217,614483],
                "gmVolume":[656447,743526],
                "csfVolume":[361434,421399],
                "totalVolume":[1611161,1736346],
                "leftVolume":[2805.97,3406.21],
                "rightVolume":[2823.63,3490.09],
                "hippoVolume":[5688.73,6837.19],
                "wmPer":[33.7,35.9],
                "gmPer":[40,43.5],
                "csfPer":[21.4,25.3],
                "wmADper":[32.5,35.8],
                "gmADper":[36.0,40.1],
                "csfADper":[30.19,25.47]


}
stdDistribution = {
    "NCgmMean":699987.29,
    "NCgmStd":43539.41,
    "ADgmMean":607775.16,
    "ADgmStd":47714.2,

    "NChippoVolumeMean":6262.95555555555,
    "NChippoVolumeStd":580.718831807753,
    "ADhippoVolumeMean":4967.65789473684,
    "ADhippoVolumeStd":1117.786090746,

    "NCgmMeanPer":41.8,
    "NCgmStdPer":1.74,
    "ADgmMeanPer":38.0,
    "ADgmStdPer":2.02,

}
def compare(svalue,a,b):
    if(svalue < a):
        return "↓"
    elif(svalue > b):
        return "↑"
    else:
        return ""
def reportBuild(featurePath,wmPath,gmPath,csfPath,hippoPath,originImagePath,tempDir):
    Volume = ""
    SurfaceArea=""
    AreaVolume=""
    Uniformity=""
    Energy=""
    Entropy=""
    Variance=""
    wmVolume=""
    gmVolume=""
    csfVolume=""
    totalVolume=""
    wmVper=""
    gmVper=""
    csfVper=""
    leftVolume=""
    rightVolume=""
    if(featurePath is not None):
        with open(featurePath,'r') as f:
            featureData = csv.DictReader(f)
            featureDict = [row for row in featureData][0]
        Volume = float(featureDict["original_shape_VoxelVolume"])
        SurfaceArea =round( float(featureDict['original_shape_SurfaceArea']),3)
        AreaVolume =round( float(featureDict["original_shape_SurfaceVolumeRatio"]),3)
        Median = round(float(featureDict['original_firstorder_Median']),3)
        Mean = round(float(featureDict['original_firstorder_Mean']),3)

        SurfaceAreaMark = compare(SurfaceArea,3728.80,4276.30)
        AreaVolumeMark = compare(AreaVolume,0.610,0.689)
        MedianMark = compare(Median,1.58,1.75)
        MeanMark = compare(Mean,1.59,1.75)


        #Uniformity = featureDict["original_firstorder_Uniformity"]
        #Energy = featureDict["original_firstorder_Energy"]
        #Entropy = featureDict["original_firstorder_Entropy"]
        #Variance = featureDict["original_firstorder_Variance"]
        hippoVolumeImagePath = os.path.join(tempDir,"hippoVolume.png")
        drawDis(u=stdDistribution["NChippoVolumeMean"],subject=Volume,xlabel="海马体积 / mm3",sig=stdDistribution["NChippoVolumeStd"],u2=stdDistribution["ADhippoVolumeMean"],sig2=stdDistribution["ADhippoVolumeStd"],savePath=hippoVolumeImagePath)
    if(wmPath is not None):
        wmImage = nib.load(wmPath)
        gmImage = nib.load(gmPath)
        csfImage = nib.load(csfPath)

        wmVolume = np.sum(wmImage.get_fdata().flatten())
        wmVolume = round(wmVolume,2)
        gmVolume = np.sum(gmImage.get_fdata().flatten())
        gmVolume = round(gmVolume,2)
        csfVolume = np.sum(csfImage.get_fdata().flatten())
        csfVolume = round(csfVolume,2)
        totalVolume = wmVolume + gmVolume + csfVolume
        totalVolume = round(totalVolume,2)

        wmVperData = float(int (wmVolume / totalVolume * 1000)) / 10
        gmVperData = float(int (gmVolume / totalVolume * 1000)) / 10
        csfVperData = float(int (csfVolume / totalVolume * 1000)) / 10
        wmVper = str(wmVperData) + "%"
        gmVper = str(gmVperData) + "%"
        csfVper = str(csfVperData) + "%"
        brainDignose = ""
        if(wmVperData < reference["wmPer"][0] ):
            brainDignose += "白质体积占比减少；"
        elif(wmVperData > reference["wmPer"][1]):
            brainDignose += "白质体积占比增加；"
        if (gmVperData < reference["gmPer"][0]):
            brainDignose += "灰质体积占比减少；"
        elif (gmVperData > reference["gmPer"][1]):
            brainDignose += "灰质体积占比增加；"
        if (csfVperData < reference["csfPer"][0]):
            brainDignose += "脑脊液体积占比减少；"
        elif (wmVperData > reference["csfPer"][1]):
            brainDignose += "脑脊液体积占比增加；"
        if(brainDignose == ""):
            brainDignose += "未见明显异常"
        VolumeDistributionImagePath = os.path.join(tempDir,"volume.png")
        drawDis(u=stdDistribution["NCgmMeanPer"],subject=gmVperData,xlabel="灰质体积占比 / % ",sig=stdDistribution["NCgmStdPer"],u2=stdDistribution['ADgmMeanPer'],sig2=stdDistribution['ADgmStdPer'],savePath=VolumeDistributionImagePath)
    hippoDignose = ""
    if(hippoPath is not None):
        hippoImage = nib.load(hippoPath)
        leftHippo = hippoImage.get_fdata()[0:91,:,:]
        rightHippo = hippoImage.get_fdata()[91:,:,:]

        leftVolume = np.sum(leftHippo.flatten())
        rightVolume = np.sum(rightHippo.flatten())
        leftVolumeMark = ""
        if(leftVolume < reference["leftVolume"][0]):
            leftVolumeMark =  "↓"
            hippoDignose += "左侧海马体积减少；"
        elif(leftVolume > reference["leftVolume"][1]):
            leftVolumeMark =  "↑"
            hippoDignose += "左侧海马体积增加；"
        rightVolumeMark = ""
        if (rightVolume < reference["rightVolume"][0]):
            rightVolumeMark = "↓"
            hippoDignose += "右侧海马体积减少；"
        elif (rightVolume > reference["rightVolume"][1]):
            rightVolumeMark = "↑"
            hippoDignose += "右侧海马体积增加；"
        if(hippoDignose == ""):
            hippoDignose += "未见明显异常"
        hippoImagePngPath = os.path.join(tempDir,"hippoimage.png")
        drawRoi(originImagePath,hippoPath,hippoImagePngPath)

    path = os.path.dirname(os.path.realpath(__file__))
    doc = DocxTemplate(os.path.join(path,"./Report.docx"))

    sd = doc.new_subdoc()
    #sd.add_paragraph(' :')
    rows = 30
    cols = 4
    table = sd.add_table(rows=rows, cols=cols,style="mystyle")
    #
    # # header
    cells = table.rows[0].cells
    cells[0].text = "指标"
    cells[1].text = "值"
    cells[2].text = "参考范围"
    cells[3].text = "备注"
    referencePath = os.path.join(path,"feature.csv")
    with open(referencePath, 'r') as f:
        refData = csv.DictReader(f)
        refDicts = [row for row in refData]
    i=1
    for ref in refDicts:
        if(i>29):
            break
        featureName = ref['feature']
        featureValue = float(featureDict[featureName])
        refDataF = str(round(float(ref['NC-mean'])-float(ref['NC-std']),2))+"~"+str(round(float(ref['NC-mean'])+float(ref['NC-std']),2))
        remark = ""
        if(featureValue < float(ref['NC-mean'])-float(ref['NC-std'])):
            remark = "↓"
        elif(featureValue > float(ref['NC-mean'])+float(ref['NC-std'])):
            remark = "↑"
        table.cell(i,0).text = featureName
        table.cell(i,1).text = str(round(featureValue,2))
        table.cell(i,2).text = str(refDataF)
        table.cell(i,3).text = remark
        i+=1

    context = {'SubjectName': "Test Subject",
               "VolumeDistributionImage": InlineImage(doc, VolumeDistributionImagePath, width=Mm(130)),
               "HippoImage": InlineImage(doc, hippoImagePngPath, width=Mm(130)),
               "HippoDistributionImage": InlineImage(doc, hippoVolumeImagePath, width=Mm(130)),
               "Volume": Volume,
               "SurfaceArea": SurfaceArea,
               "AreaVolume": AreaVolume,
               "Median": Median,
               "Mean": Mean,
               "wmVolume": wmVolume,
               "gmVolume": gmVolume,
               "csfVolume": csfVolume,
               "totalVolume": totalVolume,
               "wmVper": wmVper,
               "gmVper": gmVper,
               "csfVper": csfVper,
               "leftVolume": leftVolume,
               "rightVolume": rightVolume,
               'mytable': sd,
               "SurfaceAreaMark" : SurfaceAreaMark,
                "AreaVolumeMark" : AreaVolumeMark,
                "MedianMark" : MedianMark,
                "MeanMark" : MeanMark,
                "leftVolumeMark":leftVolumeMark,
                "rightVolumeMark":rightVolumeMark,
                "brainDignose":brainDignose,
               "hippoDignose":hippoDignose,
               "rightVolumeRef":str(reference["rightVolume"][0])+"~"+str(reference["rightVolume"][1]),
               "leftVolumeRef":str(reference["leftVolume"][0])+"~"+str(reference["leftVolume"][1]),
               }
    doc.render(context)
    doc.save(os.path.realpath(os.path.join(tempDir,os.path.basename(originImagePath)+".docx")))

def drawRoi(imgPath,roiPath,savePath):
    from matplotlib import pyplot as plt
    plotting.plot_roi(roiPath, bg_img=imgPath, title="Hippocampus", draw_cross=False, dim=0, cmap=plt.cm.autumn,output_file=savePath)

def drawDis(u,sig,subject,savePath,u2=None,sig2=None,xlabel="值",ylabel="概率"):
    import math
    from matplotlib import pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    x = np.linspace(u - 4 * sig, u + 4 * sig, 50)
    stdG = lambda x, u, sig: np.exp(-(x - u) ** 2 / (2 * sig ** 2)) / (math.sqrt(2 * math.pi) * sig)
    y_sig = stdG(x, u, sig)
    figure = plt.figure(figsize=[8,5])
    plt.plot(x, y_sig, "r-", linewidth=2, label="Normal")

    if(u2 is not None):
        x2 = np.linspace(u2 - 4 * sig2, u2 + 4 * sig2, 50)
        y_sig2 = stdG(x2, u2, sig2)
        plt.plot(x2, y_sig2, "b-", linewidth=2, label="AD")

    show_max = 'Subject Location'
    loc = (subject + subject/100, stdG(subject, u, sig))
    if u2 is not None:

        loc2 = (subject + subject/100, stdG(subject, u2, sig2))
        plt.plot(subject, stdG(subject, u2, sig2), 'ks')
        plt.annotate(show_max, xytext=loc2, xy=loc2)
    plt.xticks(size = 14)
    plt.yticks(size = 14)
    plt.plot(subject, stdG(subject, u, sig), 'ks')
    plt.annotate(show_max, xytext=loc, xy=loc)
    plt.xlabel(xlabel,fontdict={'size':14})
    plt.ylabel(ylabel,fontdict={'size':14})
    plt.legend(loc='upper right',prop={'size':14})
    plt.savefig(savePath)


if __name__ == '__main__':
    featurePath = r"D:\Develope\z\Brain\TempDir\201905241428\_featuretemp/3_AD050.nii.gz.csv"
    wmPath = r"D:\Develope\z\Brain\TempDir\201905241428\_bstemp/wm_3_AD050.nii.gz"
    gmPath = r"D:\Develope\z\Brain\TempDir\201905241428\_bstemp/gm_3_AD050.nii.gz"
    csfPath = r"D:\Develope\z\Brain\TempDir\201905241428\_bstemp/csf_3_AD050.nii.gz"
    hippoPath = r"D:\Develope\z\Brain\TempDir\201905241428\_featuretemp/3_AD050.nii.gz"
    dataTemp = r"D:\Develope\z\Brain\TempDir\201905241428\_datatemp/"
    originImagePath = "D:\Develope\z\image/3_AD050.nii"
    reportBuild(featurePath, wmPath, gmPath, csfPath, hippoPath, originImagePath, tempDir=dataTemp)