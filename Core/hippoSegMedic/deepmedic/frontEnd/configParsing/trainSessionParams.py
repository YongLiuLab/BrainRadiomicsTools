# Copyright (c) 2016, Konstantinos Kamnitsas
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the BSD license. See the accompanying LICENSE file
# or read the terms at https://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, print_function, division

from deepmedic.frontEnd.configParsing.utils import getAbsPathEvenIfRelativeIsGiven, parseAbsFileLinesInList, parseFileLinesInList, check_and_adjust_path_to_ckpt
from deepmedic.dataManagement import samplingType


class TrainSessionParameters(object) :
    
    #To be called from outside too.
    @staticmethod
    def getSessionName(sessionName) :
        return sessionName if sessionName is not None else "trainSession"
    
    #REQUIRED:
    @staticmethod
    def errorRequireChannelsTraining():
        print("ERROR: Parameter \"channelsTraining\" needed but not provided in config file. This parameter should provide paths to files, as many as the channels (modalities) of the task. Each of the files should contain a list of paths, one for each case to train on. These paths in a file should point to the .nii(.gz) files that are the corresponding channel for a patient. Please provide it in the format: channelsTraining = [\"path-to-file-for-channel1\", ..., \"path-to-file-for-channelN\"]. The paths should be given in quotes, separated by commas (list of strings, python-style). Exiting."); exit(1) 
    errReqChansTr = errorRequireChannelsTraining
    @staticmethod
    def errorRequireGtLabelsTraining():
        print("ERROR: Parameter \"gtLabelsTraining\" needed but not provided in config file. This parameter should provide the path to a file. That file should contain a list of paths, one for each case to train on. These paths should point to the .nii(.gz) files that contain the corresponding Ground-Truth labels for a case. Please provide it in the format: gtLabelsTraining = \"path-to-file\". The path should be given in quotes (a string, python-style). Exiting."); exit(1) 
    errReqGtTr = errorRequireGtLabelsTraining
    @staticmethod
    def errorRequireBatchsizeTrain():
        print("ERROR: Please provide size of batch size in train-config. See parameter \'batchsize\'. Exiting."); exit(1) 
    errReqBatchSizeTr = errorRequireBatchsizeTrain

    @staticmethod
    def errorRequirePredefinedLrSched() :
        print("ERROR: Parameter \"typeOfLearningRateSchedule\" was set to \"predefined\", but no predefined schedule was given. Please specify at which epochs to lower the Learning Rate, by providing the corresponding parameter in the format: predefinedSchedule = [epoch-for-1st-decrease, ..., epoch-for-last-decrease], where the epochs are specified by an integer > 0. Exiting."); exit(1)
    errReqPredLrSch = errorRequirePredefinedLrSched
    @staticmethod
    def errorAutoRequiresValSamples() :
        print("ERROR: Parameter \"typeOfLearningRateSchedule\" was set to \"auto\". This requires performing validation on samples throughout training, because this schedule lowers the Learning Rate when validation-accuracy plateaus. However the parameter \"performValidationOnSamplesThroughoutTraining\" was set to False in the configuration file, or was ommitted, which triggers the default value, False! Please set the parameter performValidationOnSamplesThroughoutTraining = True. You will then need to provide the path to the channels of the validation cases in the format: channelsValidation = [\"path-to-file-that-lists-paths-to-channel-1-for-every-case\", ..., \"path-to-file-that-lists-paths-to-channel-N-for-every-case\"] (python style list-of-strings)."+\
              "\t Also, you will need to provide the Ground-Truth for the validation cases, in the format:  gtLabelsValidation = \"path-to-file\", where the file lists the paths to the GT labels of each validation case. Exiting!"); exit(1)
    @staticmethod
    def errorRequireChannelsVal() :
        print("ERROR: Parameter \"channelsValidation\" was not provided, although it is required to perform validation, although validation was requested (parameters \"performValidationOnSamplesThroughoutTraining\" or \"performFullInferenceOnValidationImagesEveryFewEpochs\" was set to True). You will need to provide a list with path to files that list where the channels for each validation case can be found. The corresponding parameter must be provided in the format: channelsValidation = [\"path-to-file-that-lists-paths-to-channel-1-for-every-case\", ..., \"path-to-file-that-lists-paths-to-channel-N-for-every-case\"] (python style list-of-strings). Exiting."); exit(1)
    errReqChannsVal = errorRequireChannelsVal
    @staticmethod
    def errorReqGtLabelsVal() :
        print("ERROR: Parameter \"gtLabelsValidation\" was not provided, although it is required to perform validation on training-samples, which was requested (parameter \"performValidationOnSamplesThroughoutTraining\" was set to True). It is also useful so that the DSC score is reported if full-inference on the validation samples is performed (when parameter \"performFullInferenceOnValidationImagesEveryFewEpochs\" is set to True)! You will need to provide the path to a file that lists where the GT labels for each validation case can be found. The corresponding parameter must be provided in the format: gtLabelsValidation = \"path-to-file-that-lists-GT-labels-for-every-case\" (python style string). Exiting."); exit(1)
        
        
    #VALIDATION
    @staticmethod
    def errorReqNumberOfEpochsBetweenFullValInfGreaterThan0() :
        print("ERROR: It was requested to perform full-inference on validation images by setting parameter \"performFullInferenceOnValidationImagesEveryFewEpochs\" to True. For this, it is required to specify the number of epochs between two full-inference procedures. This number was given equal to 0. Please specify a number greater than 0, in the format: numberOfEpochsBetweenFullInferenceOnValImages = 1 (Any integer. Default is 1). Exiting!"); exit(1)
    @staticmethod
    def errorRequireNamesOfPredictionsVal() :
        print("ERROR: It was requested to perform full-inference on validation images by setting parameter \"performFullInferenceOnValidationImagesEveryFewEpochs\" to True and then save some of the results (segmentation maps, probability maps or feature maps), either manually or by default. For this, it is required to specify the path to a file, which should contain names to give to the results. Please specify the path to such a file in the format: namesForPredictionsPerCaseVal = \"./validation/validationNamesOfPredictionsSimple.cfg\" (python-style string). Exiting!"); exit(1)
    
    @staticmethod
    def errorRequireOptimizer012() :
        print("ERROR: The parameter \"sgd0orAdam1orRms2\" must be given 0,1 or 2. Omit for default. Exiting!"); exit(1)
    @staticmethod
    def errorRequireMomentumClass0Nestov1() :
        print("ERROR: The parameter \"classicMom0OrNesterov1\" must be given 0 or 1. Omit for default. Exiting!"); exit(1)
    @staticmethod
    def errorRequireMomValueBetween01() :
        print("ERROR: The parameter \"momentumValue\" must be given between 0.0 and 1.0 Omit for default. Exiting!"); exit(1)
    @staticmethod
    def errorRequireMomNonNorm0Norm1() :
        print("ERROR: The parameter \"momNonNorm0orNormalized1\" must be given 0 or 1. Omit for default. Exiting!"); exit(1)
    
    def __init__(self,
                log,
                mainOutputAbsFolder,
                folderForSessionCnnModels,
                folderForPredictionsVal,
                folderForFeaturesVal,
                num_classes,
                model_name,
                cfg):
        
        #Importants for running session.
        # From Session:
        self.log = log
        self.mainOutputAbsFolder = mainOutputAbsFolder
        
        # From Config:
        self.sessionName = self.getSessionName( cfg[cfg.SESSION_NAME] )
        
        abs_path_to_cfg = cfg.get_abs_path_to_cfg()
        abs_path_to_saved = getAbsPathEvenIfRelativeIsGiven( cfg[cfg.SAVED_MODEL], abs_path_to_cfg ) if cfg[cfg.SAVED_MODEL] is not None else None # Load pretrained model.
        self.savedModelFilepath = check_and_adjust_path_to_ckpt( self.log, abs_path_to_saved) if abs_path_to_saved is not None else None
        
        #====================TRAINING==========================
        self.filepath_to_save_models = folderForSessionCnnModels + "/" + model_name + "." + self.sessionName
        if cfg[cfg.CHANNELS_TR] is None:
            self.errReqChansTr()
        if cfg[cfg.GT_LABELS_TR] is None:
            self.errReqGtTr()
        #[[case1-ch1, ..., caseN-ch1], [case1-ch2,...,caseN-ch2]]
        listOfAListPerChannelWithFilepathsOfAllCasesTrain = [parseAbsFileLinesInList(getAbsPathEvenIfRelativeIsGiven(channelConfPath, abs_path_to_cfg)) for channelConfPath in cfg[cfg.CHANNELS_TR]]
        self.channelsFilepathsTrain = [ list(item) for item in zip(*tuple(listOfAListPerChannelWithFilepathsOfAllCasesTrain)) ] #[[case1-ch1, case1-ch2], ..., [caseN-ch1, caseN-ch2]]
        self.gtLabelsFilepathsTrain = parseAbsFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.GT_LABELS_TR], abs_path_to_cfg) )
        
        #[Optionals]
        #~~~~~~~~~Sampling~~~~~~~
        self.providedRoiMasksTrain = True if cfg[cfg.ROI_MASKS_TR] else False
        self.roiMasksFilepathsTrain = parseAbsFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.ROI_MASKS_TR], abs_path_to_cfg) ) if self.providedRoiMasksTrain else []
        
        samplingTypeToUseTr = cfg[cfg.TYPE_OF_SAMPLING_TR] if cfg[cfg.TYPE_OF_SAMPLING_TR] is not None else 3
        self.samplingTypeInstanceTrain = samplingType.SamplingType( self.log, samplingTypeToUseTr, num_classes)
        if samplingTypeToUseTr in [0,3] and cfg[cfg.PROP_OF_SAMPLES_PER_CAT_TR] is not None :
            self.samplingTypeInstanceTrain.setPercentOfSamplesPerCategoryToSample( cfg[cfg.PROP_OF_SAMPLES_PER_CAT_TR] )
        else :
            numberOfCategoriesOfSamplesTr = self.samplingTypeInstanceTrain.getNumberOfCategoriesToSample()
            self.samplingTypeInstanceTrain.setPercentOfSamplesPerCategoryToSample( [1.0/numberOfCategoriesOfSamplesTr]*numberOfCategoriesOfSamplesTr )
            
        self.paths_to_wmaps_per_sampl_cat_per_subj_train = None
        if cfg[cfg.WEIGHT_MAPS_PER_CAT_FILEPATHS_TR] is not None :
            #[[case1-weightMap1, ..., caseN-weightMap1], [case1-weightMap2,...,caseN-weightMap2]]
            self.paths_to_wmaps_per_sampl_cat_per_subj_train = [parseAbsFileLinesInList(getAbsPathEvenIfRelativeIsGiven(weightMapConfPath, abs_path_to_cfg)) for weightMapConfPath in cfg[cfg.WEIGHT_MAPS_PER_CAT_FILEPATHS_TR]]
        self.providedWeightMapsToSampleForEachCategoryTraining = self.paths_to_wmaps_per_sampl_cat_per_subj_train is not None
        
        #~~~~~~~~ Training Cycle ~~~~~~~~~~~
        self.numberOfEpochs = cfg[cfg.NUM_EPOCHS] if cfg[cfg.NUM_EPOCHS] is not None else 35
        self.numberOfSubepochs = cfg[cfg.NUM_SUBEP] if cfg[cfg.NUM_SUBEP] is not None else 20
        self.max_n_cases_per_subep_train = cfg[cfg.NUM_CASES_LOADED_PERSUB] if cfg[cfg.NUM_CASES_LOADED_PERSUB] is not None else 50
        self.n_samples_per_subep_train = cfg[cfg.NUM_TR_SEGMS_LOADED_PERSUB] if cfg[cfg.NUM_TR_SEGMS_LOADED_PERSUB] is not None else 1000
        self.batchsize_train = cfg[cfg.BATCHSIZE_TR] if cfg[cfg.BATCHSIZE_TR] is not None else errReqBatchSizeTr()
        self.num_parallel_proc_sampling = cfg[cfg.NUM_OF_PROC_SAMPL] if cfg[cfg.NUM_OF_PROC_SAMPL] is not None else 0
        
        #~~~~~~~ Learning Rate Schedule ~~~~~~~~
        
        assert cfg[cfg.LR_SCH_TYPE] in ['stable', 'predef', 'poly', 'auto', 'expon']
        self.lr_sched_params = {'type': cfg[cfg.LR_SCH_TYPE] if cfg[cfg.LR_SCH_TYPE] is not None else 'poly',
                               'predef': { 'epochs': cfg[cfg.PREDEF_SCH],
                                           'div_lr_by': cfg[cfg.DIV_LR_BY] if cfg[cfg.DIV_LR_BY] is not None else 2.0 },
                               'auto': { 'min_incr_of_val_acc_considered': cfg[cfg.AUTO_MIN_INCR_VAL_ACC] if cfg[cfg.AUTO_MIN_INCR_VAL_ACC] is not None else 0.0,
                                         'epochs_wait_before_decr': cfg[cfg.NUM_EPOCHS_WAIT] if cfg[cfg.NUM_EPOCHS_WAIT] is not None else 5,
                                         'div_lr_by': cfg[cfg.DIV_LR_BY] if cfg[cfg.DIV_LR_BY] is not None else 2.0 },
                               'poly': { 'epochs_wait_before_decr': cfg[cfg.NUM_EPOCHS_WAIT] if cfg[cfg.NUM_EPOCHS_WAIT] is not None else self.numberOfEpochs/3,
                                         'final_ep_for_sch': self.numberOfEpochs },
                               'expon': { 'epochs_wait_before_decr': cfg[cfg.NUM_EPOCHS_WAIT] if cfg[cfg.NUM_EPOCHS_WAIT] is not None else self.numberOfEpochs/3,
                                          'final_ep_for_sch': self.numberOfEpochs,
                                          'lr_to_reach_at_last_ep': cfg[cfg.EXPON_SCH][0] if cfg[cfg.EXPON_SCH] is not None else 1.0/(2**(8)),
                                          'mom_to_reach_at_last_ep': cfg[cfg.EXPON_SCH][1] if cfg[cfg.EXPON_SCH] is not None else 0.9 }
                                }
        #Predefined.
        if self.lr_sched_params['type'] == 'predef' and self.lr_sched_params['predef']['epochs'] is None :
            self.errReqPredLrSch()
        
        #~~~~~~~~~~~~~~ Augmentation~~~~~~~~~~~~~~
        self.augm_params_tr = {'hist_dist': None, 'reflect': None, 'rotate90': None}
        if cfg[cfg.AUGM_PARAMS_TR] is not None:
            for key in cfg[cfg.AUGM_PARAMS_TR]:
                self.augm_params_tr[key] = cfg[cfg.AUGM_PARAMS_TR][key] # For exact form of parameters, see ./deepmedic/dataManagement/augmentation.py
        
        #===================VALIDATION========================
        self.val_on_samples_during_train = cfg[cfg.PERFORM_VAL_SAMPLES] if cfg[cfg.PERFORM_VAL_SAMPLES] is not None else False
        if self.lr_sched_params['type'] == 'auto' and not self.val_on_samples_during_train :
            self.errorAutoRequiresValSamples()
        self.val_on_whole_volumes = cfg[cfg.PERFORM_VAL_INFERENCE] if cfg[cfg.PERFORM_VAL_INFERENCE] is not None else False
        
        #Input:
        if self.val_on_samples_during_train or self.val_on_whole_volumes :
            if cfg[cfg.CHANNELS_VAL] :
                listOfAListPerChannelWithFilepathsOfAllCasesVal = [parseAbsFileLinesInList(getAbsPathEvenIfRelativeIsGiven(channelConfPath, abs_path_to_cfg)) for channelConfPath in cfg[cfg.CHANNELS_VAL]]
                #[[case1-ch1, case1-ch2], ..., [caseN-ch1, caseN-ch2]]
                self.channelsFilepathsVal = [ list(item) for item in zip(*tuple(listOfAListPerChannelWithFilepathsOfAllCasesVal)) ]
            else :
                self.errReqChannsVal()
                
        else :
            self.channelsFilepathsVal = []
        if self.val_on_samples_during_train :
            self.gtLabelsFilepathsVal = parseAbsFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.GT_LABELS_VAL], abs_path_to_cfg) ) if cfg[cfg.GT_LABELS_VAL] is not None else self.errorReqGtLabelsVal()
        elif self.val_on_whole_volumes :
            self.gtLabelsFilepathsVal = parseAbsFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.GT_LABELS_VAL], abs_path_to_cfg) ) if cfg[cfg.GT_LABELS_VAL] is not None else []
        else : # Dont perform either of the two validations.
            self.gtLabelsFilepathsVal = []
        self.providedGtVal = True if self.gtLabelsFilepathsVal is not None else False
        
        #[Optionals]
        self.providedRoiMasksVal = True if cfg[cfg.ROI_MASKS_VAL] is not None else False #For fast inf.
        self.roiMasksFilepathsVal = parseAbsFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.ROI_MASKS_VAL], abs_path_to_cfg) ) if self.providedRoiMasksVal else []
        
        #~~~~~Validation on Samples~~~~~~~~
        self.n_samples_per_subep_val = cfg[cfg.NUM_VAL_SEGMS_LOADED_PERSUB] if cfg[cfg.NUM_VAL_SEGMS_LOADED_PERSUB] is not None else 3000
        self.batchsize_val_samples = cfg[cfg.BATCHSIZE_VAL_SAMPL] if cfg[cfg.BATCHSIZE_VAL_SAMPL] is not None else 50
        
        #~~~~~~~~~ Sampling (Validation) ~~~~~~~~~~~
        samplingTypeToUseVal = cfg[cfg.TYPE_OF_SAMPLING_VAL] if cfg[cfg.TYPE_OF_SAMPLING_VAL] is not None else 1
        self.samplingTypeInstanceVal = samplingType.SamplingType( self.log, samplingTypeToUseVal, num_classes)
        if samplingTypeToUseVal in [0,3] and cfg[cfg.PROP_OF_SAMPLES_PER_CAT_VAL] is not None:
            self.samplingTypeInstanceVal.setPercentOfSamplesPerCategoryToSample( cfg[cfg.PROP_OF_SAMPLES_PER_CAT_VAL] )
        else :
            numberOfCategoriesOfSamplesVal = self.samplingTypeInstanceVal.getNumberOfCategoriesToSample()
            self.samplingTypeInstanceVal.setPercentOfSamplesPerCategoryToSample( [1.0/numberOfCategoriesOfSamplesVal]*numberOfCategoriesOfSamplesVal )
            
        self.paths_to_wmaps_per_sampl_cat_per_subj_val = None
        if cfg[cfg.WEIGHT_MAPS_PER_CAT_FILEPATHS_VAL] is not None:
            #[[case1-weightMap1, ..., caseN-weightMap1], [case1-weightMap2,...,caseN-weightMap2]]
            self.paths_to_wmaps_per_sampl_cat_per_subj_val = [parseAbsFileLinesInList(getAbsPathEvenIfRelativeIsGiven(weightMapConfPath, abs_path_to_cfg)) for weightMapConfPath in cfg[cfg.WEIGHT_MAPS_PER_CAT_FILEPATHS_VAL]]
        self.providedWeightMapsToSampleForEachCategoryValidation = self.paths_to_wmaps_per_sampl_cat_per_subj_val is not None
        
        #~~~~~~Full inference on validation image~~~~~~
        self.num_epochs_between_val_on_whole_volumes = cfg[cfg.NUM_EPOCHS_BETWEEN_VAL_INF] if cfg[cfg.NUM_EPOCHS_BETWEEN_VAL_INF] is not None else 1
        if self.num_epochs_between_val_on_whole_volumes == 0 and self.val_on_whole_volumes :
            self.errorReqNumberOfEpochsBetweenFullValInfGreaterThan0()
        
        self.batchsize_val_whole = cfg[cfg.BATCHSIZE_VAL_WHOLE] if cfg[cfg.BATCHSIZE_VAL_WHOLE] is not None else 10
        
        #predictions
        self.saveSegmentationVal = cfg[cfg.SAVE_SEGM_VAL] if cfg[cfg.SAVE_SEGM_VAL] is not None else True
        self.saveProbMapsBoolPerClassVal = cfg[cfg.SAVE_PROBMAPS_PER_CLASS_VAL] if (cfg[cfg.SAVE_PROBMAPS_PER_CLASS_VAL] is not None and cfg[cfg.SAVE_PROBMAPS_PER_CLASS_VAL] != []) else [True]*num_classes
        self.filepathsToSavePredictionsForEachPatientVal = None #Filled by call to self.makeFilepathsForPredictionsAndFeatures()
        self.suffixForSegmAndProbsDictVal = cfg[cfg.SUFFIX_SEGM_PROB_VAL] if cfg[cfg.SUFFIX_SEGM_PROB_VAL] is not None else {"segm": "Segm", "prob": "ProbMapClass"}
        #features:
        self.saveIndividualFmImagesVal = cfg[cfg.SAVE_INDIV_FMS_VAL] if cfg[cfg.SAVE_INDIV_FMS_VAL] is not None else False
        self.saveMultidimensionalImageWithAllFmsVal = cfg[cfg.SAVE_4DIM_FMS_VAL] if cfg[cfg.SAVE_4DIM_FMS_VAL] is not None else False
        if self.saveIndividualFmImagesVal == True or self.saveMultidimensionalImageWithAllFmsVal == True:
            indices_fms_per_pathtype_per_layer_to_save = [cfg[cfg.INDICES_OF_FMS_TO_SAVE_NORMAL_VAL]] +\
                                                         [cfg[cfg.INDICES_OF_FMS_TO_SAVE_SUBSAMPLED_VAL]] +\
                                                         [cfg[cfg.INDICES_OF_FMS_TO_SAVE_FC_VAL]]
            self.indices_fms_per_pathtype_per_layer_to_save = [item if item is not None else [] for item in indices_fms_per_pathtype_per_layer_to_save] #By default, save none.
        else:
            self.indices_fms_per_pathtype_per_layer_to_save = None
        self.filepathsToSaveFeaturesForEachPatientVal = None #Filled by call to self.makeFilepathsForPredictionsAndFeatures()
        
        #Output:
        #Given by the config file, and is then used to fill filepathsToSavePredictionsForEachPatient and filepathsToSaveFeaturesForEachPatient.
        self.namesToSavePredictionsAndFeaturesVal = parseFileLinesInList( getAbsPathEvenIfRelativeIsGiven(cfg[cfg.NAMES_FOR_PRED_PER_CASE_VAL], abs_path_to_cfg) ) if cfg[cfg.NAMES_FOR_PRED_PER_CASE_VAL] else None #CAREFUL: Here we use a different parsing function!
        if not self.namesToSavePredictionsAndFeaturesVal and self.val_on_whole_volumes and (self.saveSegmentationVal or True in self.saveProbMapsBoolPerClassVal or self.saveIndividualFmImagesVal or self.saveMultidimensionalImageWithAllFmsVal) :
            self.errorRequireNamesOfPredictionsVal()
            
        #===================== OTHERS======================
        #Preprocessing
        self.padInputImagesBool = cfg[cfg.PAD_INPUT] if cfg[cfg.PAD_INPUT] is not None else True
        
        #Others useful internally or for reporting:
        self.numberOfCasesTrain = len(self.channelsFilepathsTrain)
        self.numberOfCasesVal = len(self.channelsFilepathsVal)
        self.run_input_checks = cfg[cfg.RUN_INP_CHECKS] if cfg[cfg.RUN_INP_CHECKS] is not None else True
        
        #HIDDENS, no config allowed for these at the moment:
        
        # Re-weight samples in the cost function *on a per-class basis*: Type of re-weighting and training schedule.
        # E.g. to exclude a class, or counter class imbalance.
        # "type": string/None, "prms": any/None, "schedule": [ min_epoch, max_epoch ]
        # Type, prms combinations: "freq", None || "per_c", [0., 2., 1., ...] (as many as classes)
        # "schedule": Constant before epoch [0], linear change towards equal weight (=1) until epoch [1], constant equal weights (=1) afterwards.
        self.reweight_classes_in_cost = cfg[cfg.W_C_IN_COST] if cfg[cfg.W_C_IN_COST] is not None else {"type": None, "prms": None, "schedule": [0, self.numberOfEpochs]}
        if self.reweight_classes_in_cost["type"] == "per_c":
            assert len(self.reweight_classes_in_cost["prms"]) == num_classes
        
        self._makeFilepathsForPredictionsAndFeaturesVal( folderForPredictionsVal, folderForFeaturesVal )
        
        #====Optimization=====
        self.learningRate = cfg[cfg.LRATE] if cfg[cfg.LRATE] is not None else 0.001
        self.optimizerSgd0Adam1Rms2 = cfg[cfg.OPTIMIZER] if cfg[cfg.OPTIMIZER] is not None else 2
        if self.optimizerSgd0Adam1Rms2 == 0 :
            self.b1Adam = "placeholder"; self.b2Adam = "placeholder"; self.eAdam = "placeholder";
            self.rhoRms = "placeholder"; self.eRms = "placeholder";
        elif self.optimizerSgd0Adam1Rms2 == 1 :
            self.b1Adam = cfg[cfg.B1_ADAM] if cfg[cfg.B1_ADAM] is not None else 0.9 #default in paper and seems good
            self.b2Adam = cfg[cfg.B2_ADAM] if cfg[cfg.B2_ADAM] is not None else 0.999 #default in paper and seems good
            self.eAdam = cfg[cfg.EPS_ADAM] if cfg[cfg.EPS_ADAM] is not None else 10**(-8)
            self.rhoRms = "placeholder"; self.eRms = "placeholder";
        elif self.optimizerSgd0Adam1Rms2 == 2 :
            self.b1Adam = "placeholder"; self.b2Adam = "placeholder"; self.eAdam = "placeholder";
            self.rhoRms = cfg[cfg.RHO_RMS] if cfg[cfg.RHO_RMS] is not None else 0.9 #default in paper and seems good
            self.eRms = cfg[cfg.EPS_RMS] if cfg[cfg.EPS_RMS] is not None else 10**(-4) # 1e-6 was the default in the paper, but blew up the gradients in first try. Never tried 1e-5 yet.
        else :
            self.errorRequireOptimizer012()
            
        self.classicMom0Nesterov1 = cfg[cfg.MOM_TYPE] if cfg[cfg.MOM_TYPE] is not None else 1
        if self.classicMom0Nesterov1 not in [0,1]:
            self.errorRequireMomentumClass0Nestov1()
        self.momNonNormalized0Normalized1 = cfg[cfg.MOM_NORM_NONNORM] if cfg[cfg.MOM_NORM_NONNORM] is not None else 1
        if self.momNonNormalized0Normalized1 not in [0,1] :
            self.errorRequireMomNonNorm0Norm1()
        self.momentumValue = cfg[cfg.MOM] if cfg[cfg.MOM] is not None else 0.6
        if self.momentumValue < 0. or self.momentumValue > 1:
            self.errorRequireMomValueBetween01()
            
        #==Regularization==
        self.L1_reg_weight = cfg[cfg.L1_REG] if cfg[cfg.L1_REG] is not None else 0.000001
        self.L2_reg_weight = cfg[cfg.L2_REG] if cfg[cfg.L2_REG] is not None else 0.0001
        
        #============= HIDDENS ==============
        # Indices of layers that should not be trained (kept fixed).
        layersToFreezePerPathwayType =  [cfg[cfg.LAYERS_TO_FREEZE_NORM],
                                         cfg[cfg.LAYERS_TO_FREEZE_SUBS],
                                         cfg[cfg.LAYERS_TO_FREEZE_FC]]
        indicesOfLayersToFreezeNorm = [ l-1 for l in layersToFreezePerPathwayType[0] ] if layersToFreezePerPathwayType[0] is not None else []
        indicesOfLayersToFreezeSubs = [ l-1 for l in layersToFreezePerPathwayType[1] ] if layersToFreezePerPathwayType[1] is not None else indicesOfLayersToFreezeNorm
        indicesOfLayersToFreezeFc = [ l-1 for l in layersToFreezePerPathwayType[2] ] if layersToFreezePerPathwayType[2] is not None else []
        # Three sublists, one per pathway type: Normal, Subsampled, FC. eg: [[0,1,2],[0,1,2],[]
        self.indicesOfLayersPerPathwayTypeToFreeze = [ indicesOfLayersToFreezeNorm, indicesOfLayersToFreezeSubs, indicesOfLayersToFreezeFc ]
        
        self.losses_and_weights = cfg[cfg.LOSSES_WEIGHTS] if cfg[cfg.LOSSES_WEIGHTS] is not None else {"xentr": 1.0, "iou": None, "dsc": None}
        assert True in [ self.losses_and_weights[k] is not None for k in ["xentr", "iou", "dsc"] ]
        
        self._backwards_compat_with_deprecated_cfg(cfg)
        
        """
        #NOTES: variables that have to do with number of pathways: 
                self.indicesOfLayersPerPathwayTypeToFreeze (="all" always currently. Hardcoded)
                indices_fms_per_pathtype_per_layer_to_save (Repeat subsampled!)
        """
        
    def _backwards_compat_with_deprecated_cfg(self, cfg):
        # Augmentation
        if cfg[cfg.REFL_AUGM_PER_AXIS] is not None:
            self.augm_params_tr['reflect'] = [ 0.5 if bool else 0. for bool in cfg[cfg.REFL_AUGM_PER_AXIS] ]
        if cfg[cfg.PERF_INT_AUGM_BOOL] == True:
            self.augm_params_tr['hist_dist'] = {'shift': {'mu': cfg[cfg.INT_AUGM_SHIF_MUSTD][0], 'std': cfg[cfg.INT_AUGM_SHIF_MUSTD][1]},
                                                'scale': {'mu': cfg[cfg.INT_AUGM_MULT_MUSTD][0], 'std': cfg[cfg.INT_AUGM_MULT_MUSTD][1]} }
    
    def _makeFilepathsForPredictionsAndFeaturesVal( self,
                                                    absPathToFolderForPredictionsFromSession,
                                                    absPathToFolderForFeaturesFromSession
                                                    ) :
        self.filepathsToSavePredictionsForEachPatientVal = []
        self.filepathsToSaveFeaturesForEachPatientVal = []
        if self.namesToSavePredictionsAndFeaturesVal is not None : # standard behavior
            for case_i in range(self.numberOfCasesVal) :
                filepathForCasePrediction = absPathToFolderForPredictionsFromSession + "/" + self.namesToSavePredictionsAndFeaturesVal[case_i]
                self.filepathsToSavePredictionsForEachPatientVal.append( filepathForCasePrediction )
                filepathForCaseFeatures = absPathToFolderForFeaturesFromSession + "/" + self.namesToSavePredictionsAndFeaturesVal[case_i]
                self.filepathsToSaveFeaturesForEachPatientVal.append( filepathForCaseFeatures )
        else : # Names for predictions not given. Special handling...
            if self.numberOfCasesVal > 1 : # Many cases, create corresponding namings for files.
                for case_i in range(self.numberOfCasesVal) :
                    self.filepathsToSavePredictionsForEachPatientVal.append( absPathToFolderForPredictionsFromSession + "/pred_case" + str(case_i) + ".nii.gz" )
                    self.filepathsToSaveFeaturesForEachPatientVal.append( absPathToFolderForPredictionsFromSession + "/pred_case" + str(case_i) + ".nii.gz" )
            else : # Only one case. Just give the output prediction folder, the io.py will save output accordingly.
                self.filepathsToSavePredictionsForEachPatientVal.append( absPathToFolderForPredictionsFromSession )
                self.filepathsToSaveFeaturesForEachPatientVal.append( absPathToFolderForPredictionsFromSession )
    
    
    def get_path_to_load_model_from(self):
        return self.savedModelFilepath
    
    def print_params(self) :
        logPrint = self.log.print3
        logPrint("")
        logPrint("=============================================================")
        logPrint("========= PARAMETERS FOR THIS TRAINING SESSION ==============")
        logPrint("=============================================================")
        logPrint("Session's name = " + str(self.sessionName))
        logPrint("Model will be loaded from save = " + str(self.savedModelFilepath))
        logPrint("~~Output~~")
        logPrint("Main output folder = " + str(self.mainOutputAbsFolder))
        logPrint("Path and filename to save trained models = " + str(self.filepath_to_save_models))
        
        logPrint("~~~~~~~~~~~~~~~~~~Generic Information~~~~~~~~~~~~~~~~")
        logPrint("Number of Cases for Training = " + str(self.numberOfCasesTrain))
        logPrint("Number of Cases for Validation = " + str(self.numberOfCasesVal))
        
        logPrint("~~~~~~~~~~~~~~~~~~Training parameters~~~~~~~~~~~~~~~~")
        logPrint("Filepaths to Channels of the Training Cases = " + str(self.channelsFilepathsTrain))
        logPrint("Filepaths to Ground-Truth labels of the Training Cases = " + str(self.gtLabelsFilepathsTrain))
        
        logPrint("~~ Sampling (train) ~~")
        logPrint("Region-Of-Interest Masks provided = " + str(self.providedRoiMasksTrain))
        logPrint("Filepaths to ROI Masks of the Training Cases = " + str(self.roiMasksFilepathsTrain))
        
        logPrint("Type of Sampling = " + str(self.samplingTypeInstanceTrain.getStringOfSamplingType()) + " ("+ str(self.samplingTypeInstanceTrain.getIntSamplingType()) + ")")
        logPrint("Sampling Categories = " + str(self.samplingTypeInstanceTrain.getStringsPerCategoryToSample()) )
        logPrint("Percent of Samples to extract per Sampling Category = " + str(self.samplingTypeInstanceTrain.getPercentOfSamplesPerCategoryToSample()))
        logPrint("Provided Weight-Maps, pointing where to focus sampling for each category (if False, samples will be extracted based on GT and ROI) = " + str(self.providedWeightMapsToSampleForEachCategoryTraining))
        logPrint("Paths to weight-Maps for sampling of each category = " + str(self.paths_to_wmaps_per_sampl_cat_per_subj_train))
        
        logPrint("~~Training Cycle~~")
        logPrint("Number of Epochs = " + str(self.numberOfEpochs))
        logPrint("Number of Subepochs per epoch = " + str(self.numberOfSubepochs))
        logPrint("Number of cases to load per Subepoch (for extracting the samples for this subepoch) = " + str(self.max_n_cases_per_subep_train))
        logPrint("Number of Segments loaded per subepoch for Training = " + str(self.n_samples_per_subep_train) + ". NOTE: This number of segments divided by the batch-size defines the number of optimization-iterations that will be performed every subepoch!")
        logPrint("Batch size (train) = " + str(self.batchsize_train))
        logPrint("Number of parallel processes for sampling = " + str(self.num_parallel_proc_sampling))
        
        logPrint("~~Learning Rate Schedule~~")
        logPrint("Type of schedule = " + str(self.lr_sched_params['type']))
        logPrint("[Predef] Predefined schedule of epochs when the LR will be lowered = " + str(self.lr_sched_params['predef']['epochs']))
        logPrint("[Predef] When decreasing Learning Rate, divide LR by = " + str(self.lr_sched_params['predef']['div_lr_by']) )
        logPrint("[Poly] Initial epochs to wait before lowering LR = " + str(self.lr_sched_params['poly']['epochs_wait_before_decr']) )
        logPrint("[Poly] Final epoch for the schedule = " + str(self.lr_sched_params['poly']['final_ep_for_sch']) )
        logPrint("[Auto] Initial epochs to wait before lowering LR = " + str(self.lr_sched_params['auto']['epochs_wait_before_decr']) )
        logPrint("[Auto] When decreasing Learning Rate, divide LR by = " + str(self.lr_sched_params['auto']['div_lr_by']) )
        logPrint("[Auto] Minimum increase in validation accuracy (0. to 1.) that resets the waiting counter = " + str(self.lr_sched_params['auto']['min_incr_of_val_acc_considered']))
        logPrint("[Expon] (Deprecated) parameters = " + str(self.lr_sched_params['expon']))
        
        logPrint("~~Data Augmentation During Training~~")
        logPrint("Mu and std for shift and scale of histograms = " + str(self.augm_params_tr['hist_dist']))
        logPrint("Probabilities of reflecting each axis = " + str(self.augm_params_tr['reflect']))
        logPrint("Probabilities of rotating planes 0/90/180/270 degrees = " + str(self.augm_params_tr['rotate90']))
        
        logPrint("~~~~~~~~~~~~~~~~~~Validation parameters~~~~~~~~~~~~~~~~")
        logPrint("Perform Validation on Samples throughout training? = " + str(self.val_on_samples_during_train))
        logPrint("Perform Full Inference on validation cases every few epochs? = " + str(self.val_on_whole_volumes))
        logPrint("Filepaths to Channels of the Validation Cases (Req for either of the above) = " + str(self.channelsFilepathsVal))
        logPrint("Provided Ground-Truth for Validation = " + str(self.providedGtVal) + ". NOTE: Required for Val on samples. Not Req for Full-Inference, but DSC will be reported if provided.")
        logPrint("Filepaths to Ground-Truth labels of the Validation Cases = " + str(self.gtLabelsFilepathsVal))
        logPrint("Provided ROI masks for Validation = " + str(self.providedRoiMasksVal) + ". NOTE: Validation-sampling and Full-Inference will be limited within this mask if provided. If not provided, Negative Validation samples will be extracted from whole volume, except if advanced-sampling is enabled, and the user provided separate weight-maps for sampling.")
        logPrint("Filepaths to ROI masks for Validation Cases = " + str(self.roiMasksFilepathsVal))
        
        logPrint("~~~~~~~Validation on Samples throughout Training~~~~~~~")
        logPrint("Number of Segments loaded per subepoch for Validation = " + str(self.n_samples_per_subep_val))
        logPrint("Batch size (val on samples) = " + str(self.batchsize_val_samples))
        
        logPrint("~~ Sampling (val) ~~")
        logPrint("Type of Sampling = " + str(self.samplingTypeInstanceVal.getStringOfSamplingType()) + " ("+ str(self.samplingTypeInstanceVal.getIntSamplingType()) + ")")
        logPrint("Sampling Categories = " + str(self.samplingTypeInstanceVal.getStringsPerCategoryToSample()) )
        logPrint("Percent of Samples to extract per Sampling Category = " + str(self.samplingTypeInstanceVal.getPercentOfSamplesPerCategoryToSample()))
        logPrint("Provided Weight-Maps, pointing where to focus sampling for each category (if False, samples will be extracted based on GT and ROI) = " + str(self.providedWeightMapsToSampleForEachCategoryValidation))
        logPrint("Paths to weight-maps for sampling of each category = " + str(self.paths_to_wmaps_per_sampl_cat_per_subj_val))
        
        logPrint("~~~~~Validation with Full Inference on Validation Cases~~~~~")
        logPrint("Perform Full-Inference on Val. cases every that many epochs = " + str(self.num_epochs_between_val_on_whole_volumes))
        logPrint("Batch size (val on whole volumes) = " + str(self.batchsize_val_whole))
        logPrint("~~Predictions (segmentations and prob maps on val. cases)~~")
        logPrint("Save Segmentations = " + str(self.saveSegmentationVal))
        logPrint("Save Probability Maps for each class = " + str(self.saveProbMapsBoolPerClassVal))
        logPrint("Filepaths to save results per case = " + str(self.filepathsToSavePredictionsForEachPatientVal))
        logPrint("Suffixes with which to save segmentations and probability maps = " + str(self.suffixForSegmAndProbsDictVal))
        logPrint("~~Feature Maps~~")
        logPrint("Save Feature Maps = " + str(self.saveIndividualFmImagesVal))
        logPrint("Save FMs in a 4D-image = " + str(self.saveMultidimensionalImageWithAllFmsVal))
        logPrint("Min/Max Indices of FMs to visualise per pathway-type and per layer = " + str(self.indices_fms_per_pathtype_per_layer_to_save))
        logPrint("Filepaths to save FMs per case = " + str(self.filepathsToSaveFeaturesForEachPatientVal))
        
        logPrint("~~Optimization~~")
        logPrint("Initial Learning rate = " + str(self.learningRate))
        logPrint("Optimizer to use: SGD(0), Adam(1), RmsProp(2) = " + str(self.optimizerSgd0Adam1Rms2))
        logPrint("Parameters for Adam: b1= " + str(self.b1Adam) + ", b2=" + str(self.b2Adam) + ", e= " + str(self.eAdam) )
        logPrint("Parameters for RmsProp: rho= " + str(self.rhoRms) + ", e= " + str(self.eRms) )
        logPrint("Momentum Type: Classic (0) or Nesterov (1) = " + str(self.classicMom0Nesterov1))
        logPrint("Momentum Non-Normalized (0) or Normalized (1) = " + str(self.momNonNormalized0Normalized1))
        logPrint("Momentum Value = " + str(self.momentumValue))
        logPrint("~~Costs~~")
        logPrint("Loss functions and their weights = " + str(self.losses_and_weights))
        logPrint("Reweight samples in cost on a per-class basis = " + str(self.reweight_classes_in_cost))
        logPrint("L1 Regularization term = " + str(self.L1_reg_weight))
        logPrint("L2 Regularization term = " + str(self.L2_reg_weight))
        logPrint("~~Freeze Weights of Certain Layers~~")
        logPrint("Indices of layers from each type of pathway that will be kept fixed (first layer is 0):")
        logPrint("Normal pathway's layers to freeze = "+ str(self.indicesOfLayersPerPathwayTypeToFreeze[0]))
        logPrint("Subsampled pathway's layers to freeze = "+ str(self.indicesOfLayersPerPathwayTypeToFreeze[1]))
        logPrint("FC pathway's layers to freeze = "+ str(self.indicesOfLayersPerPathwayTypeToFreeze[2]))
        
        logPrint("~~~~~~~~~~~~~~~~~~Other Generic Parameters~~~~~~~~~~~~~~~~")
        logPrint("Check whether input data has correct format (can slow down process) = " + str(self.run_input_checks))
        logPrint("~~Pre Processing~~")
        logPrint("Pad Input Images = " + str(self.padInputImagesBool))
        
        logPrint("========== Done with printing session's parameters ==========")
        logPrint("=============================================================\n")
        
    def get_args_for_train_routine(self) :
        
        args = [self.log,
                self.filepath_to_save_models,
                
                self.val_on_samples_during_train,
                {"segm": self.saveSegmentationVal, "prob": self.saveProbMapsBoolPerClassVal},
                
                self.filepathsToSavePredictionsForEachPatientVal,
                self.suffixForSegmAndProbsDictVal,
                
                self.channelsFilepathsTrain,
                self.channelsFilepathsVal,
                
                self.gtLabelsFilepathsTrain,
                self.providedGtVal,
                self.gtLabelsFilepathsVal,
                
                self.providedWeightMapsToSampleForEachCategoryTraining, #Always true, since either GT labels or advanced-mask-where-to-pos
                self.paths_to_wmaps_per_sampl_cat_per_subj_train,
                self.providedWeightMapsToSampleForEachCategoryValidation, #If false, corresponding samples will be extracted uniformly from whole image.
                self.paths_to_wmaps_per_sampl_cat_per_subj_val,
                
                self.providedRoiMasksTrain,
                self.roiMasksFilepathsTrain,
                self.providedRoiMasksVal,
                self.roiMasksFilepathsVal,
                
                self.numberOfEpochs,
                self.numberOfSubepochs,
                self.max_n_cases_per_subep_train,
                self.n_samples_per_subep_train,
                self.n_samples_per_subep_val,
                self.num_parallel_proc_sampling,
                
                #-------Sampling Type---------
                self.samplingTypeInstanceTrain,
                self.samplingTypeInstanceVal,
                self.batchsize_train,
                self.batchsize_val_samples,
                self.batchsize_val_whole,
                
                #-------Preprocessing-----------
                self.padInputImagesBool,
                #-------Data Augmentation-------
                self.augm_params_tr,
                 
                # --- Validation on whole volumes ---
                self.val_on_whole_volumes,
                self.num_epochs_between_val_on_whole_volumes,
                
                #--------For FM visualisation---------
                self.saveIndividualFmImagesVal,
                self.saveMultidimensionalImageWithAllFmsVal,
                self.indices_fms_per_pathtype_per_layer_to_save,
                self.filepathsToSaveFeaturesForEachPatientVal,
                
                #-------- Others --------
                self.run_input_checks
                ]
        return args
    
    def get_args_for_trainer(self) :
        args = [self.log,
                self.indicesOfLayersPerPathwayTypeToFreeze,
                self.losses_and_weights,
                # Regularisation
                self.L1_reg_weight,
                self.L2_reg_weight,
                # Cost Schedules
                #Weighting Classes differently in the CNN's cost function during training:
                self.reweight_classes_in_cost
                ]
        return args
    
    def get_args_for_optimizer(self) :
        args = [self.log,
                self.optimizerSgd0Adam1Rms2,
                
                self.lr_sched_params,
                
                self.learningRate,
                self.momentumValue,
                self.classicMom0Nesterov1, 
                self.momNonNormalized0Normalized1,
                self.b1Adam,
                self.b2Adam,
                self.eAdam,
                self.rhoRms,
                self.eRms
                ]
        return args





