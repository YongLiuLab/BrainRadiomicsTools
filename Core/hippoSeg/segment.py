import os
from Core import setting
from Core.hippoSeg import networkSegmentation as net
from backports import configparser as ConfigParser
from Core.setting import path
from Core.utils import checkDir
import nibabel as nib
import numpy as np
def segment(filename_input,directory_output ,Type=False):
    '''
    :param filename_input: input dir or filename
    :param directory_output: output dir name
    :param Type: True ,use dir mode / False use file mode
    :return:
    '''
    inipath = setting.LiviaNet_iniPath
    modelname = setting.LiviaNet_modelPath
    print(inipath)
    print(modelname)
    print(filename_input)
    filepath = filename_input

    iniFile = resini(inipath)

    # True THE Whole dir
    try:
        if Type:
            num = str([i for i in range(len(os.listdir(filename_input)))])
            iniFile.write(filepath, "imagesFolder")
            images = checkDir(filepath)
            for image in images:
                idata = nib.load(image)
                data = idata.get_fdata()
                affine = idata.affine
                data = (data - np.mean(data.flatten()))/np.std(data.flatten())

                nib.save(nib.Nifti1Image(data,affine).to_filename(image))
        else:
            
            idata = nib.load(filepath)
            data = idata.get_fdata()
            affine = idata.affine
            
            data = (data - np.mean(data.flatten()))/np.std(data.flatten())
            nib.save(nib.Nifti1Image(data,affine),filepath)

            getNum = lambda file_path,file_name : os.listdir(file_path).index(file_name)
            num = [getNum(os.path.dirname(filepath), os.path.basename(filepath))]  # 获得文件的索引值
            iniFile.write(os.path.dirname(filepath), "imagesFolder")
        # resindex = resini(inipath)  # 实例化resindex
        iniFile.write(str(num),"indexestosegment")  # 将 indexestosegment 写入ini文件
        roiPath = os.path.join(path,"hippoSeg","roi")
        iniFile.write(roiPath,"roifolder")
        net.startTesting(modelname, inipath, directory_output)
    except Exception as e:
        print(e)
        return 1
    return 0
class resini():
    def __init__(self, path):
        self.path = path
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.path)

    def write(self, value,item):
        if self.config.has_option('Segmentation Images', item):
            self.config.set('Segmentation Images', item, value)
            # value = os.path.dirname(value) # 获取最后一个/前的地址
            # self.config.set('Segmentation Images', 'imagesFolder', value)
            self.config.write(open(self.path, 'w'))
            print(value)  # 输出改变的ini文件对应的值
        else:
            print('parse ini fail')