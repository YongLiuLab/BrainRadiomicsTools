import os
batchTempDir = "./TempDir"
path = os.path.split(os.path.realpath(__file__))[0]
print("Core Path :",path)
LiviaNet_iniPath = os.path.join(path,"hippoSeg/Segmentation.ini")
LiviaNet_modelPath = os.path.join(path,"hippoSeg/liviaTest_Epoch16")