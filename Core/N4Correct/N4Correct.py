import SimpleITK as sitk
import os
import numpy as np
from Core.utils import make_headmask
from Core.setting import path
import subprocess
import nibabel as nib
def N4correctBatch(inputDir,outputDir,isNormal,isBFC):
    images = os.listdir(inputDir)
    imageList = []
    for i in range(len(images)):
        if images[i].split(".")[-1] == 'nii' or images[i].split(".")[-2:0] == 'nii.gz':
            imageList.append(images[i])
    del images
    for image in imageList:
        N4correct(os.path.join(inputDir,image),os.path.join(outputDir,image),isNorm=isNormal,isBFC=isBFC)
def N4correctWin(inputImage,outputImage ,maskImage=None,isNorm=False,isBFC=True):
    exPath = os.path.join(path,"N4Correct","N4BiasFieldCorrection.exe")
    if maskImage == None:
        maskImagePath = os.path.join(os.path.dirname(outputImage),"../","tempMask.nii")
        make_headmask(sitk.ReadImage(inputImage),output=maskImagePath)

    inputImage = os.path.abspath(os.path.join(path,"../",inputImage))
    if (not isBFC):
        image = nib.load(inputImage)
        data = image.get_fdata()
    if (isBFC):
        task = subprocess.Popen('%s -d 3 -i %s -x %s -o %s ' % (exPath, inputImage, maskImagePath, outputImage), shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        msg = ''
        for line in task.stdout.readlines():
            msg += line.decode("gb2312")
        status = task.wait()
        print(msg)

        image = nib.load(outputImage)
        data = image.get_fdata()
    if(isNorm):
        data = (data - np.mean(data.flatten()))/np.std(data.flatten())
    nib.Nifti1Image(data,image.affine).to_filename(outputImage)

def N4correct(inputImage,outputImage ,maskImage=None,isNorm=False,isBFC=True):
    import SimpleITK as sitk
    sitk.ProcessObject_SetGlobalWarningDisplay(True)
    input = sitk.ReadImage(inputImage)
    spacing = input.GetSpacing()
    direction = input.GetDirection()
    origin = input.GetOrigin()
    if isBFC:
        if maskImage is not None:
            mask = sitk.ReadImage(maskImage, sitk.sitkUInt8 )
        else:
            mask = make_headmask(input)
            maskImage = sitk.GetImageFromArray(mask)

            #maskImage = sitk.OtsuThreshold( input, 0, 1, 200 )
            maskImage.SetDirection(input.GetDirection())
            maskImage.SetOrigin(input.GetOrigin())
            maskImage.SetSpacing(input.GetSpacing())
            #sitk.Show(maskImage*255)
        input = sitk.Cast( input, sitk.sitkFloat32 )
        mask = sitk.Cast( maskImage , sitk.sitkUInt8)
        corrector = sitk.N4BiasFieldCorrectionImageFilter()
        #corrector.SetDebug(True)
        corrector.SetNumberOfThreads(4)
        corrector.SetDebug(True)
        corrector.SetMaximumNumberOfIterations([50]*4)

        print("input : origin:",input.GetOrigin(),"Mask : origin:",mask.GetOrigin())
        output = corrector.Execute(input)

        del  corrector
        del  mask
    if isNorm:
        data = sitk.GetArrayFromImage(output)
        data = (data - np.mean(data.flatten()))/np.std(data.flatten())
        output = sitk.GetImageFromArray(data)
    output.SetDirection(direction)
    output.SetSpacing(spacing)
    output.SetOrigin(origin)
    sitk.WriteImage(output, outputImage)

    del sitk