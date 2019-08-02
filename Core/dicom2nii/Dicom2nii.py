import dicom2nifti
import os
import subprocess
from shutil import move, rmtree
from Core.setting import globalTempDir,path
file = "cot1mprnssagiso.nii"
def convertDicom(original_dicom_directory, output_file):
    print("Input dicom directory : ",original_dicom_directory)
    print("Output nii file path : ",output_file)
    try:
        dicom2nifti.dicom_series_to_nifti(original_dicom_directory, output_file, reorient_nifti=False)
    # Registration.reg(output_file,output_file)
    except Exception:
        return 1
    return 0
def convertDicoms(original_dicom_directory, output_file):
    temp = os.path.join(globalTempDir, "/Dicom2niiTemp/")
    if not os.path.exists(temp):
        os.makedirs(temp)
    else:
        rmtree(temp)
        os.makedirs(temp)
    ConvertProgram = os.path.join(path, "../Binary/dcm2nii.exe")
    print(ConvertProgram)
    task = subprocess.Popen(
        '%s -a y -d n -e n -f n -g n -f n -o %s %s' % (ConvertProgram, temp, original_dicom_directory), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    msg = ''
    for line in task.stdout.readlines():
        msg += line.decode("gb2312")
    status = task.wait()
    # print(stdout.decode("gb2312"))
    # print(msg)
    #print("dicom2nii.py line 30!")
    try:
        move(os.path.join(temp, file), output_file)
        #rmtree(temp)
    except Exception:
        print("File Error")
        return 1
    return 0

