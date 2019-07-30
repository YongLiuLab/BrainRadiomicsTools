import os
import numpy
import numpy as np
import nibabel as nib
import pdb
import scipy.io

from loadData import load_nii

def saveImageAsNifti(imageToSave,
                     imageName,
                     imageOriginalName,
                     imageType):
    printFileNames = False

    if printFileNames == True:
        print(" ... Saving image in {}".format(imageName))

    [imageData, img_proxy] = load_nii(imageOriginalName, printFileNames)

    # Generate the nii file
    niiToSave = nib.Nifti1Image(imageToSave, img_proxy.affine)
    niiToSave.set_data_dtype(imageType)

    dim = len(imageToSave.shape)
    zooms = list(img_proxy.header.get_zooms()[:dim])
    if len(zooms) < dim:
        zooms = zooms + [1.0] * (dim - len(zooms))

    niiToSave.header.set_zooms(zooms)
    nib.save(niiToSave, imageName)

    print "... Image succesfully saved..."

