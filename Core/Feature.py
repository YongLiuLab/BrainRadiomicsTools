#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from collections import OrderedDict
import csv
from datetime import datetime
import logging
from multiprocessing import cpu_count, Pool, freeze_support
import os
import shutil
import threading
import SimpleITK as sitk
import radiomics

from radiomics.featureextractor import RadiomicsFeatureExtractor

from os import walk, path
from sys import argv
import numpy
notDisplayType = ['diagnostics_Versions_PyRadiomics',
                  'diagnostics_Versions_Numpy',
                  'diagnostics_Versions_SimpleITK',
                  'diagnostics_Versions_PyWavelet',
                  'diagnostics_Versions_Python',
                  'diagnostics_Image-original_Hash',
                  "diagnostics_Mask-original_Hash",
                  "Reader",
                  "Patient",
                  "label"
                  ]
logging.getLogger('radiomics.batch').debug('Logging init')


class info_filter(logging.Filter):
    def __init__(self, name):
        super(info_filter, self).__init__(name)
        self.level = logging.ERROR

    def filter(self, record):
        if record.levelno >= self.level:
            return True
        if record.name == self.name and record.levelno >= logging.ERROR:
            return True
        return False


rLogger = radiomics.logger
LOG = os.path.join(os.getcwd(), 'log.txt', )
logHandler = logging.FileHandler(filename=LOG, mode='w')
logHandler.setLevel(logging.DEBUG)
logHandler.setFormatter(logging.Formatter('%(levelname)-.1s: (%(threadName)s) %(name)s: %(message)s'))
rLogger.addHandler(logHandler)
rLogger.setLevel(logging.DEBUG)
logger = logging.getLogger('radiomics.batch')
outputhandler = rLogger.handlers[0]  # Handler printing to the output
outputhandler.setFormatter(logging.Formatter('[%(asctime)-.19s] (%(threadName)s) %(name)s: %(message)s'))
outputhandler.setLevel(logging.DEBUG)  # Ensures that INFO messages are being passed to the filter
outputhandler.addFilter(info_filter('radiomics.batch'))

class feature:
    def __init__(self, outputfile, cases, settings={}, tempDir="_TEMP", root=os.getcwd(), notDisplayType={}):
        self.setting = settings
        self.ROOT = root
        self.TEMP_DIR = tempDir
        self._filename = outputfile
        self.notDisplayType = notDisplayType
        self.cases = cases
        self.NUM_OF_WORKERS = cpu_count() - 5
        self.inputHeader = 0
        self.t_list = []
        if self.NUM_OF_WORKERS < 1:
            self.NUM_OF_WORKERS = 1
        self.REMOVE_TEMP_DIR = True
        if (len(self.cases) < self.NUM_OF_WORKERS):
            self.NUM_OF_WORKERS = len(self.cases)
        if not os.path.isdir(os.path.join(self.ROOT, self.TEMP_DIR)):
            print('Creating temporary output directory %s', os.path.join(self.ROOT, self.TEMP_DIR))
            os.mkdir(os.path.join(self.ROOT, self.TEMP_DIR))
        #self.pool = Pool(self.NUM_OF_WORKERS)

    def _calculate(self, case):
        ptLogger = logging.getLogger('radiomics.batch')
        feature_vector = OrderedDict(case)
        # to suggest the temp file is valid/invalid
        p=0

        try:
            # set thread name to patient name
            threading.current_thread().name = case['Subject']
            filename = r'features_' + '_' + str(case['Patient']) + '.csv'
            output_filename = os.path.join(self.ROOT, self.TEMP_DIR, filename)
            newFeatureVector = {}
            if os.path.isfile(output_filename):
                with open(output_filename, 'w') as outputFile:
                    reader = csv.reader(outputFile)
                    try:
                        headers = reader.rows[0]
                        values = reader.rows[1]
                    except Exception:
                        p=1
                        rLogger.debug("the temp file ", output_filename, "is damaging,please delete it")
            if os.path.isfile(output_filename) and p ==0:
                with open(output_filename, 'w') as outputFile:
                    reader = csv.reader(outputFile)
                    try:
                        headers = reader.rows[0]
                        values = reader.rows[1]
                        feature_vector = OrderedDict(zip(headers, values))
                        # filter some feature that isn't number
                        for featureName in feature_vector.keys():
                            if featureName not in self.notDisplayType:
                                if not isinstance(feature_vector[featureName], (list, dict, tuple)):
                                    newFeatureVector[featureName] = feature_vector[featureName]
                    except Exception:
                        rLogger.debug("Erro ++:::++The temp file", output_filename, "is damaging,please delete it")
                        return {"Subject": case['Subject']}
                ptLogger.info('Subject %s  already processed...', case['Patient'])
            else:
                t = datetime.now()
                imageFilepath = case['Image']  # Required
                maskFilepath = case['Mask']  # Required
                label = case.get('Label', None)  # Optional
                extractor = RadiomicsFeatureExtractor(**(self.setting))
                extractor.enableImageTypes(Original={},
                                           LoG={},
                                           Wavelet={},
                                           SquareRoot={},
                                           Square={},
                                           Logarithm={},
                                           Gradient={},
                                           Exponential={},
                                           LBP3D={},
                                           )
                extractor.enableAllFeatures()
                feature_vector.update(extractor.execute(imageFilepath, maskFilepath), label=label)
                # filter some feature that isn't number
                for featureName in feature_vector.keys():
                    if featureName not in notDisplayType:
                        if not isinstance(feature_vector[featureName], (list, dict, tuple)):
                            newFeatureVector[featureName] = feature_vector[featureName]
                # Store results in temporary separate files to prevent write conflicts
                # This allows for the extraction to be interrupted. Upon restarting, already processed cases are found in the
                # TEMP_DIR directory and loaded instead of re-extracted
                with open(output_filename, 'w') as outputFile:
                    writer = csv.DictWriter(outputFile, fieldnames=list(newFeatureVector.keys()), lineterminator='\n')
                    writer.writeheader()
                    writer.writerow(newFeatureVector)
                # Display message
                delta_t = datetime.now() - t
                ptLogger.info('Subject %s read by %s processed in', case['Patient'], delta_t)
        except Exception as e:
            ptLogger.error("Compute Error ! Error ! Error ! Error !\r\n"+str(e))
            newFeatureVector["diagnostics_Image-original_Mean"] = "Calculate ERRO ! , please check your data!"
            newFeatureVector["Image"]=feature_vector.get("Image")
            newFeatureVector["Mask"] = feature_vector.get("Mask")
            newFeatureVector["Subject"] =feature_vector.get("Subject")
        finally:
            return newFeatureVector

    def run(self, Q=None):
        mainLogger = logging.getLogger('radiomics.batch')
        threading.current_thread().name = 'Main'
        cnt = 1
        results = []
        for result in self.pool.imap_unordered(self._calculate, self.cases):
            print('processing the images,done   %d/%d...' % (cnt, len(self.cases)))
            cnt += 1
            if Q != None:
                Q.put(int((cnt - 1) / len(self.cases) * 100))
            results.append(result)
        try:
            results = sorted(results, key=lambda r: r.get("Subject"))
        except Exception as e:
            mainLogger.debug(str(e))
        finally:
            try:
                self._writeResults(results)
            except Exception:
                mainLogger.debug('Error |||| storing results into single file!', str(e))

    def singleCal(self, case):
        print("case",case)
        image = sitk.ReadImage(str(case.get("Image")))
        mask = sitk.ReadImage(str(case.get("Mask")))
        mask = sitk.Cast(mask, sitk.sitkInt8)
        featureVector = OrderedDict(case)
        featureVector.update(self.extractor.execute(image, mask))
        with open(self._filename, 'a+') as csvfile:
            if (self.inputHeader == 0):
                for featureName in featureVector.keys():
                    if featureName not in self.notDisplayType:
                        if not isinstance(featureVector[featureName], (list, dict, tuple)):
                            self.t_list.append(featureName)
                writer = csv.DictWriter(csvfile, fieldnames=self.t_list, lineterminator='\n')
                writer.writeheader()
                self.inputHeader = 1
            else:
                writer = csv.DictWriter(csvfile, fieldnames=self.t_list, lineterminator='\n')
            new = {k: v for k, v in featureVector.items() if k in self.t_list}
            writer.writerow(new)

    def singleRun(self):
        self.extractor = RadiomicsFeatureExtractor(**self.setting)
        self.extractor.enableImageTypes(Original={},
                                        LoG={},
                                        Wavelet={},
                                        SquareRoot={},
                                        Square={},
                                        Logarithm={},
                                        Gradient={},
                                        Exponential={},
                                        LBP3D={},
                                        )
        i = 1
        for case in self.cases:
            print("\rdealing with the " + str(i) + "/" + str(len(self.cases)) + " image...")
            i += 1
            self.singleCal(case)
        print("calculate successfully!")

    def _writeResults(self, results):
        with open(self._filename, mode='w') as outputFile:
            writer = csv.DictWriter(outputFile,
                                    fieldnames=list(results[0].keys()),
                                    restval='',
                                    extrasaction='raise',
                                    lineterminator='\n')
            writer.writeheader()
            writer.writerows(results)
        if self.REMOVE_TEMP_DIR:
            logger.info('Removing temporary directory %s (contains individual case results files)',
                        os.path.join(self.ROOT, self.TEMP_DIR))
            shutil.rmtree(os.path.join(self.ROOT, self.TEMP_DIR))
            print("completed!")

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


def getFilesDir(imagePath, maskPath):
    whitelist = ['nii']
    imageList = []
    # 指定想要统计的文件类型
    maskList = []
    case = []
    # 遍历文件, 递归遍历文件夹中的所有
    for parent, dirnames, filenames in walk(imagePath):
        # for dirname in dirnames:
        #    getFile(os.path.join(parent,dirname)) #递归
        for filename in sorted(filenames):
            ext = filename.split('.')[-1]
            # 只统计指定的文件类型，略过一些log和cache文件
            if ext in whitelist:
                imageList.append(path.join(parent, filename))
    for parent, dirnames, filenames in walk(maskPath):
        for filename in sorted(filenames):
            ext = filename.split('.')[-1]
            # 只统计指定的文件类型，略过一些log和cache文件
            if ext in whitelist:
                maskList.append(path.join(parent, filename))
    for i, m in zip(imageList, maskList):
        case.append({"Subject": os.path.basename(i),
                     "Patient": os.path.basename(i),
                     "Image": i,
                     'Mask': m,
                     })
    return case


def getFilesFile(INPUTCSV):
    cases = []
    try:
        with open(INPUTCSV, 'r') as inFile:
            cr = csv.DictReader(inFile, lineterminator='\n')
            cases = []
            for row_idx, row in enumerate(cr, start=1):
                if 'Patient' not in row:
                    row['Patient'] = row_idx
                cases.append(row)
    except Exception:
        print("CSV OPEN FAILED! Please check your source file")
        exit()
    return cases


if __name__ == '__main__':
    #freeze_support()
    pool = Pool(cpu_count() - 1)
    if (len(argv) < 2):
        print("the arg is not valid!")
        exit()
    type = argv[1]
    cases = []
    if (str(type) == '-f'):
        if (len(argv) != 4):
            print("the argv is not valid! please check your input")
            exit()
        caseFile = argv[2]
        if (not os.path.isfile(caseFile)):
            print("the source csv is not exist!")
            exit()
        cases = getFilesFile(caseFile)
        OUTPUTCSV = argv[3]
        print("loading CSV..")
    elif (str(type) == '-d'):
        if (len(argv) != 5):
            print("the argv is not valid! please check your input")
            exit()
        imagePath = argv[2]
        maskPath = argv[3]
        cases = getFilesDir(imagePath, maskPath)
        OUTPUTCSV = argv[4]
        print("scanning the files...")
    # Ensure the entire extraction is handled on 1 thread
    sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(1)
    for case in cases:
        a = os.path.isfile(case['Image'])
        b = os.path.isfile(case['Mask'])
        if (not os.path.isfile(case['Image']) or not os.path.isfile(case['Mask'])):
            print("the source image is not exist ,please check your input csv file!")
            exit(0)
    settings = {}
    settings['binWidth'] = 25
    settings['label'] = 1
    settings['resampledPixelSpacing'] = None  # [3,3,3] is an example for defining resampling (voxels with size 3x3x3mm)
    settings['interpolator'] = sitk.sitkBSpline
    settings['sigma'] = numpy.arange(5., 0., -.5)[::1]
    #settings['geometryTolerance']=2.
    settings['correctMask']= True
    Feature = feature(cases=cases, settings=settings, notDisplayType=notDisplayType, outputfile=OUTPUTCSV)
    Feature.singleRun()
