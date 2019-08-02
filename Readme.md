# BrainRadiomicsTools 

  BrainRadiomicsTools is a radiomics tool that includes multiple brain image processing tools.It has many functions 
  such as registration、N4 bias correction、hippocampus segment and feature calculating.Now it can automatically 
  segment and calculate about 2000 radiomics features of the hippocampus.
  **The feature about this tool is that it has a good user interface,you can do all the work with the mouse.**
  
## Install

  The tools is a python based program,it can execute in Windows now(some function may error in Linux and Mac OS),
  The installation script is not completed yet, but here is a file `environment.yaml` describing which python packages are required for this tool.
  
  It is recommended to use Anaconda(Miniconda) for environment configuration,the most important package is theano,there will be
  some problem in the installation of theano.The key of the installation is installing mingw by conda.
  
  Use the `python Main.py` to run tool after completing the dependency package installation.

## User Interface

![image](https://github.com/gourdchen/BrainRadiomicsTools/images/main.png)

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
1. Hippocampus Segment
   `by https://github.com/josedolz/LiviaNET`
2. Brain Segment(Wm,Gm,Csf)
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
Documentation will update later.

## References
````
[1] Chen, Hao, et al. "VoxResNet: Deep Voxelwise Residual Networks for Volumetric Brain Segmentation." arXiv preprint arXiv:1608.05895 (2016).
[2] Dolz J , Desrosiers C , Ayed I B . 3D fully convolutional networks for subcortical segmentation in MRI: A large-scale study[J]. NeuroImage, 2017:S1053811917303324.
````
## Licence
This program is covered by the Apache License 2.0.