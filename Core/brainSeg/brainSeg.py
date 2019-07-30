import os
import chainer
import numpy as np
import nibabel as nib
from .model import VoxResNet
from .utils import crop_patch, load_nifti, feedforward

def brainSeg(test_df,output_path,model="./models/model9900.vrn",input_shape=[80,80,80],output_shape=[60,60,60],n_tiles=[4,4,4]):
    path = os.path.abspath(__file__)
    model_path = os.path.join(os.path.dirname(path),model)
    vrn = VoxResNet(2, 4)
    chainer.serializers.load_npz(model_path, vrn)

    for image_path in test_df["image"]:
        image, affine = load_nifti(image_path, with_affine=True)
        output = feedforward(
            vrn,
            image,
            input_shape,
            output_shape,
            n_tiles,
            4
        )
        print("组织分割获得了结果，开始计算概率")
        output /= np.sum(output, axis=0, keepdims=True)
        print("概率计算成功！")
        #data = np.float32(output).transpose(1, 2, 3, 0)
        gm_data  = output[2,0:182,0:218,0:182]
        wm_data  = output[3,0:182,0:218,0:182]
        csf_data = output[1,0:182,0:218,0:182]
        # 去单文件模式，传如的ouput_path 是文件名，这里直接赋值
        # if(mode == 0):
        #     gm_path = output_path
        # 传入的输出文件夹 batch模式和dir 模式

        gm_path = os.path.join(output_path,'gm_'+os.path.basename(image_path))

        wm_path = os.path.join(output_path,"wm_"+os.path.basename(image_path))

        csf_path = os.path.join(output_path, "csf_" + os.path.basename(image_path))
        nib.save(
            nib.Nifti1Image(gm_data, affine),
            gm_path
        )
        nib.save(
                nib.Nifti1Image(wm_data, affine),
                wm_path
            )
        nib.save(
                nib.Nifti1Image(csf_data, affine),
                csf_path
            )
        return wm_path,gm_path,csf_path