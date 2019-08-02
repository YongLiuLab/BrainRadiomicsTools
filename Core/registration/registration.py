import os
import subprocess
from Core.setting import path,regTempDir
def registration(flo,res,ref=os.path.join(path,"../data/Ref.nii"),aff=os.path.join(regTempDir,"temp.txt"),Queue = None,onlyRigid=False):
    '''
    :param flo:
    :param res:
    :param ref: options
    :param aff: options
    :param Queue: 
    :return:
    '''
    if not os.path.exists(regTempDir):
        os.mkdir(regTempDir)
    p1 = os.path.join(path,"..","Binary/reg_aladin.exe")
    p2 = os.path.join(path,"..","Binary/reg_f3d.exe")
    if(not os.path.isfile(ref)):
        ref = os.path.join(path,"..","data/Ref.nii")
    if onlyRigid:
        task = subprocess.Popen('%s -ref %s -flo %s -aff %s -res %s '% (p1, ref, flo, aff,res), shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        msg = ''
        for line in task.stdout.readlines():
            msg += line.decode("gb2312")
        status = task.wait()
        print('---------------------------------aladin_ouput-----------------------------------')
        print(msg)
        print('--------------------------------------------------------------------------------')
        return 0
    task  = subprocess.Popen('%s -ref %s -flo %s -aff %s -res ../temp.nii' %  (p1,ref,flo,aff), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    msg = ''
    for line in task.stdout.readlines():
        msg += line.decode("gb2312")
    status = task.wait()
    print(msg)
    task2 = subprocess.Popen('%s -ref %s -flo %s -aff %s -res %s'% (p2 ,ref,flo,aff,res ), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    msg = ''
    for line in task2.stdout.readlines():
        msg += line.decode("gb2312")
    status = task2.wait()
    print(msg)
    return 0
def getFiles(path):
    whitelist = ['nii','nii.gz']
    imageList = []
    for parent, dirnames, filenames in os.walk(path):
        for filename in filenames:
            ext = filename.split('.')[-1]
            if ext in whitelist:
                imageList.append(os.path.join(parent, filename))
    return imageList