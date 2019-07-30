import SimpleITK as sitk
from skimage import  morphology,measure
import numpy as np
import nibabel as nib
import os
def checkDir(path):
    '''
    :param path: dir path
    :return: [0] / [1]  0->there is some images in the dir 1-> there is none image
    '''
    images= []
    if not os.path.exists(path):
        return images
    for image in os.listdir(path):
        if image.endswith("nii") or image.endswith("nii.gz"):
          images.append(image)
    return images
def checkFile(path):
    '''
    :param path: file path
    :return: 0 / 1  0->the file is a valid nifti  1->the file is not a valid nifti
    '''
    if not os.path.exists(path):
        return 1
    if path.endswith("nii") or path.endswith("nii.gz"):
        return 0
    else:
        return 1
def make_headmask(image,  idx_method = 'Otsu' ,output = None):
    # 通过nii格式文件自动提取含颅骨的脑部mask
    # 输入：path-nii文件路径，path_save-自动保存mask路径，若为""则不输出，idx_method-阈值计算方法
    # 输出：生成的mask的ndarray数据，如果path_save非空会自动进行保存
    threshold_filters = {'Otsu': sitk.OtsuThresholdImageFilter(),
                     'Triangle' : sitk.TriangleThresholdImageFilter(),
                     'Huang' : sitk.HuangThresholdImageFilter(),
                     'MaxEntropy' : sitk.MaximumEntropyThresholdImageFilter()}

    thresh_filter = threshold_filters[idx_method]
    thresh_filter.SetInsideValue(0)
    thresh_filter.SetOutsideValue(1)
    thresh_img = thresh_filter.Execute(image)
    thresh_value = thresh_filter.GetThreshold()
    data = sitk.GetArrayFromImage(image)
    data_thresh = data >= thresh_value
    temp = data_thresh
    times = 5
    for i in range(times):
        temp = morphology.dilation(temp, selem=None, out=None, shift_x=False, shift_y=False)
    for j in range(times):
        temp = morphology.erosion(temp, selem=None, out=None, shift_x=False, shift_y=False)

    regions = temp
    regions = morphology.remove_small_holes(regions, area_threshold = 200*100*100, connectivity = 1)
    regions = regions.astype(np.float)
    if output is not None:
        newImage = sitk.GetImageFromArray(regions)
        newImage.SetSpacing(image.GetSpacing())
        newImage.SetOrigin(image.GetOrigin())
        newImage.SetDirection(image.GetDirection())
        sitk.WriteImage(newImage,output)
    return regions


def cleanImage(imagePath,outputPath):
    '''
    :param imagePath:
    :param outputPath:
    :return: 去除label中的杂点，将左右海马合一，用于batch中的提取feature之前
    '''
    image = nib.load(imagePath)
    segmentation = image.get_fdata()
    data = np.zeros((182, 218, 182))
    label = segmentation.copy()
    label[label > 0] = 1
    regions = measure.label(label)
    for i in range(0, np.max(regions.flatten()) + 1):
        if (np.size(np.where(regions == i)) > 500):
            data[np.where(regions == i)] = 1
    del label
    # save_vol(data, files[-(case_idx + 1)], "results/2" + model_name)
    segmentation = data * segmentation
    segmentation[segmentation > 1 ] = 1
    nib.Nifti1Image(segmentation,image.affine).to_filename(outputPath)

if __name__ == '__main__':
    image = sitk.ReadImage("D:\Data\data-PL_S\img/1_NC001.nii")
    make_headmask(image)