import os

# path ->  directory Core 
path = os.path.split(os.path.realpath(__file__))[0]
selectRootPath = os.path.join(path,"../../")

globalTempDir = os.path.join(path,"../","TempDir")
regTempDir = os.path.join(globalTempDir,"regTemp")






print("Core Path :",path)
print("globalTempDir :",globalTempDir)

LiviaNet_iniPath = os.path.join(path,"hippoSeg/Segmentation.ini")
LiviaNet_modelPath = os.path.join(path,"hippoSeg/liviaTest_Epoch16")