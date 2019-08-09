# BrainRadiomicsTools

  BrainRadiomicsTools is a radiomics tool that includes multiple brain image processing tools.It has many functions 
  such as registration、N4 bias correction、hippocampus segment and feature calculating.Now it can automatically 
  segment and calculate about 2000 radiomics features of the hippocampus.
  **The feature about this tool is that it has a good user interface,you can do all the work with the mouse.**
  
## Install

  The tools is a python based program,it can execute in Windows now(some function may error in Linux and Mac OS),
  The installation script is not completed yet, but here is a file `environment.yaml` and `requirement.txt` describing which python packages are required for this tool.
  
  It is recommended to use Anaconda(Miniconda) for environment configuration,the most important package is theano,there will be
  some problem in the installation of theano.The key of the installation is installing mingw by conda.

  1. If you don't have conda envirment,please install the Anaconda or Miniconda
  2. Open the CMD.exe and use conda to create a new env such as : `conda create -n brainTools python=3.6`
  3. Then activate the conda env : `conda activate brainTools`
  4. Install the mingw by conda : `conda install mingw libpython -y`
  5. Install the packages by pip :  `pip install -r requirement.txt`

  In the end, ensure the new env is activated and use the `python Main.py` to run tool after completing the dependency package installation.

## User Interface

![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/main.png)

## Function
#### Preprocessing
1. dicom2nifti
   ` by dicom2nifti python package`
2. registration
   `by NiftyReg`
3. brain extraction
   `by FSL BET`
4. N4 bias correction
   `by ANTs / SimpleITK`
#### Segmentation
Segmentation functions include hippocampus segmentation and brain segmentation.The two neural networks are trained by inhouse datasets, and tools use the trained models.
1. Hippocampus Segmentation  
   `by https://github.com/josedolz/LiviaNET`
   
2. Brain Tissue Segmentation(Wm,Gm,Csf)  
   `by https://github.com/Ryo-Ito/brain_segmentation`
#### Feature Calculating
Calculate the radiomics features `by pyradiomics`.  
Enable all the features and the following 9 image types,the inputs include the origin image and the ROI.  
Because of some problems about configure file, now the features can not be customized,and it will update later.
 ````
    Original  
    LoG
    Wavelet
    SquareRoot
    Square
    Logarithm
    Gradient
    Exponential
    LBP3D
 ````
More about the pyradiomics,you can see the documentation of it:  https://pyradiomics.readthedocs.io/en/latest/
#### Analysis
A comparison of the parameters of the input image is performed using an inhouse dataset as a reference (beta).  
A detailed analysis report is given on the input image based on the reference range of brain volume and radiomics features
 derived from the inhouse datasets.
## Documentation
There are many functions in the software,each of them can be used independently,so it is very flexible to use this software.It is recommended to use *batch* to process images,and you can also use  *function module* to process images.  
### Batch 
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/batch.png)  

*Batch* can call all the function of the program,and you can use *batch* as follows:  
1. Check the function you want by checking the checkbox on the left.
2. Choose the input and ouput directory by click the button on the right.
3. Click the Start button and wait for the completion.

### Function module
The most of function modules have two operating mode: *single file* and *directory batch*,
you can switch the mode by checking the radio button in the top of the window.It is worth to notice that each module has only one function,such as the *Hippocampus segmentation* only do the hippocampus segment without any preprocessing.
#### Dicom2Nifti
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/dicom.png)
The input is the directory of the dicom image file and the output is the Nifti image file.
#### Registration
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/reg.png)
The input is the original image or directory of the original image file, the output is the registered image,if you do not choose the `ref image`.we will use the `MMNI ICBM-152(182*218*182 mm)` to register your image.
#### Brain extraction
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/bet.png)
The input is the image or directory of the image file, the output is the image with the brain and the mask of brain.
#### Bias field correction
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/bfc.png)
The input is the image or directory of the image file, the ouput is the processed image,You can choose to whether to do bias field correction and normalization.
#### Hippocampus segmentation
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/hs.png)
The input is the image or directory of the image file, the ouput is the mask of the hippocampus.The input need to be registerd with `MMNI ICBM-152(182*218*182 mm)` (roughly is ok).
#### Brain tissue segmentation
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/bs.png)
The input is the image or directory of the origin image file, the ouput is the probability segmentation of gm, wm and csf. The input need to be registerd with `MMNI ICBM-152(182*218*182 mm)` (roughly is ok).
#### Feature caculating
![image](https://github.com/YongLiuLab/BrainRadiomicsTools/blob/master/images/feature.png)
The input is the image or directory of the image file, the ROI and image must have a one-to-one correspondence.  
If you input one image, you have to input one mask file, and the parameters of nifti file between the image and the ROI is the same. If your input is a directory, the ROI must be a directory, and the sequence of the image in the image directory is the same as the sequence of the ROI in the ROI directory. 
The ouput is a csv file, one file occupies one row, and features arranged in columns.
## Operation Example

## References
````
[1] Chen, Hao, et al. "VoxResNet: Deep Voxelwise Residual Networks for Volumetric Brain Segmentation." arXiv preprint arXiv:1608.05895 (2016).
[2] Dolz J , Desrosiers C , Ayed I B . 3D fully convolutional networks for subcortical segmentation in MRI: A large-scale study[J]. NeuroImage, 2017:S1053811917303324.
````
## Licence
This program is covered by the Apache License 2.0.