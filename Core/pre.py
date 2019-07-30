import nipy
from nipy.algorithms import interpolation,resample,registration,segmentation
from nipy.core.image.image_spaces import (make_xyz_image,
                                          xyz_affine)

if __name__ == '__main__':
    niters = 25
    beta = 0.4
    ngb_size = 6
    #mask_img = nipy.load_image("D:/reg/mask.nii")
    #img = nipy.load_image("D:\\Develope\\data-PL_S\\img\\1_NC001.nii")
    img = nipy.load_image("D:\\data\\reg\\rch2better.nii")
    mask_img = nipy.load_image("D:\\data\\reg\\mask.nii")
    mask = img.get_data() > 0
    S  = segmentation.BrainT1Segmentation(img.get_data(),mask, model='3k',
                        niters=niters, beta=beta, ngb_size=ngb_size,convert=False)

    # Save label image

    outfile = 'hard_classif2.nii'
    nipy.save_image(make_xyz_image(S.label, xyz_affine(img), 'scanner'),
               outfile)

    # img = nipy.load_image("D:/reg/ch2bet.nii")
    # ref = nipy.load_image("D:/reg/MNI152_T1_1mm.nii")
    # image = resample.resample_img2img(img,target=ref)
    # nipy.save_image(image,"D:/reg/Regch2bet.nii")