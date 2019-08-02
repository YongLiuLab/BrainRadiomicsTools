import os
from dipy.align.reslice import reslice
import nibabel as nib
from scipy.ndimage.filters import gaussian_filter
import SimpleITK as sitk
import numpy as np
import pandas as pd
from Core.brainSeg import brainSeg
import time
def preprocess_img(inputfile, output_preprocessed, zooms=[1,1,1]):
    img = nib.load(inputfile)
    data = img.get_data()
    affine = img.affine
    #The last value of header.get_zooms() is the time between scans in milliseconds; this is the equivalent of voxel size on the time axis.
    zoom = img.header.get_zooms()[:3]
    data, affine = reslice(data, affine, zoom, zooms, 1)
    data = np.squeeze(data)
    #填充256*256*256的图像，在后部进行填2
    data[data < 0 ] = 0
    data = np.pad(data, [(0, 218 - len_) for len_ in data.shape], "constant")
    
    data_sub = data - gaussian_filter(data, sigma=1)
    img = sitk.GetImageFromArray(np.copy(data_sub))
    img = sitk.AdaptiveHistogramEqualization(img)
    data_clahe = sitk.GetArrayFromImage(img)[:, :, :, None]
    data = np.concatenate((data_clahe, data[:, :, :, None]), 3)
    data = (data - np.mean(data, (0, 1, 2))) / np.std(data, (0, 1, 2))
    assert data.ndim == 4, data.ndim
    #assert np.allclose(np.mean(data, (0, 1, 2)), 0.), np.mean(data, (0, 1, 2))
    #assert np.allclose(np.std(data, (0, 1, 2)), 1.), np.std(data, (0, 1, 2))
    data = np.float32(data)

    img = nib.Nifti1Image(data, affine)
    nib.save(img, output_preprocessed)
def preprocess_label(inputfile,
                     output_label,
                     n_classes=4,
                     zooms=[1,1,1],
                     df=None,
                     input_key=None,
                     output_key=None):
    img = nib.load(inputfile)
    data = img.get_data()
    affine = img.affine
    zoom = img.header.get_zooms()[:3]
    data, affine = reslice(data, affine, zoom, zooms, 0)
    data = np.squeeze(data)
    data = np.pad(data, [(0, 256 - len_) for len_ in data.shape], "constant")

    if df is not None:
        tmp = np.zeros_like(data)
        for target, source in zip(df[output_key], df[input_key]):
            tmp[np.where(data == source)] = target
        data = tmp
    data = np.int32(data)
    print(inputfile)
    assert np.max(data) < n_classes
    img = nib.Nifti1Image(data, affine)
    nib.save(img, output_label)

def runSeg(image_path,output_path,wm_path=None,csf_path=None):
    tmp_path = os.path.join(os.path.dirname(image_path),'_tmp',os.path.basename(image_path))
    if(not os.path.exists(os.path.dirname(tmp_path))):
        os.mkdir(os.path.dirname(tmp_path))
    print(time.strftime("%H:%M:%S", time.localtime())," Start image processing")
    preprocess_img(image_path,tmp_path)
    print(time.strftime("%H:%M:%S", time.localtime())," Complete image processing")
    image = {}
    image['image'] = tmp_path
    image['subject'] = os.path.basename(tmp_path)
    image['weight'] = 1.0
    data = []
    data.append(image)
    df = pd.DataFrame(data)
    WmLabelPath, GMLabelPath, CsfLabelPath = brainSeg(df,output_path)
    #for subject,label in zip(sorted(os.listdir(image_path)),sorted(os.listdir(label_path))):
    #     preprocess_img(os.path.join(image_path,subject),os.path.join(process_path,'img',subject))
     #    preprocess_label(os.path.join(label_path,label),os.path.join(process_path,'label',label))

    return WmLabelPath,GMLabelPath,CsfLabelPath
def batchSeg(image_path,output_path):
    tmp_path = os.path.join(os.path.dirname(image_path), '_tmp_process')
    for image in sorted(os.listdir(image_path)):
        preprocess_img(image,os.path.join(tmp_path,os.path.basename(image)))
    data = []

    for file in sorted(os.listdir(tmp_path)):
        image = {}
        image["image"] = os.path.join(tmp_path,file)
        image["subject"] = file
        image["weight"] = 1.0
        data.append(image)
    df = pd.DataFrame(data)
    brainSeg(df, output_path, model="./models/model9900.vrn")

