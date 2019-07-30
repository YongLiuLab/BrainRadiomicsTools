# Copyright (c) 2016, Konstantinos Kamnitsas
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the BSD license. See the accompanying LICENSE file
# or read the terms at https://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, print_function, division

import os
import sys
import time
import numpy as np
import math
import random
import traceback
import multiprocessing
import signal
import collections

from deepmedic.dataManagement.io import loadVolume
from deepmedic.dataManagement.preprocessing import calculateTheZeroIntensityOf3dImage, padCnnInputs
from deepmedic.neuralnet.pathwayTypes import PathwayTypes as pt
from deepmedic.dataManagement.augmentation import augment_patch

# Order of calls:
# getSampledDataAndLabelsForSubepoch
#    get_random_subjects_to_train_subep
#    get_num_samples_per_cat_per_subj
#    load_subj_and_get_samples
#        load_imgs_of_subject
#        sample_coords_of_segments
#        extractSegmentGivenSliceCoords
#            getImagePartFromSubsampledImageForTraining
#    shuffleSegmentsOfThisSubepoch

# Main sampling process during training. Executed in parallel while training on a batch on GPU.
# Called from training.do_training()
def getSampledDataAndLabelsForSubepoch( log,
                                        train_or_val,
                                        num_parallel_proc,
                                        run_input_checks,
                                        cnn3d,
                                        max_n_cases_per_subep,
                                        n_samples_per_subep,
                                        sampling_type,
                                        
                                        paths_per_chan_per_subj,
                                        paths_to_lbls_per_subj,
                                        
                                        provided_mask,
                                        paths_to_masks_per_subj,
                                        
                                        provided_weightmaps_per_sampl_cat,
                                        paths_to_wmaps_per_sampl_cat_per_subj,
                                        
                                        pad_input_imgs,
                                        augm_params
                                        ):
    # Returns: channelsOfSegmentsForSubepochArrayPerPathway - List of arrays, one per pathway. Each array [N_samples, Channs, R,C,Z]
    #        lblsForPredictedPartOfSegmentsForSubepochArray - Array of shape: [N_samples, R_out, C_out, Z_out)
    
    id_str = "[SAMPLER-TR|PID:"+str(os.getpid())+"]" if train_or_val == "train" else "[SAMPLER-VAL|PID:"+str(os.getpid())+"]"
    start_time_sampling = time.time()
    training_or_validation_str = "Training" if train_or_val == "train" else "Validation"
    
    log.print3(id_str+" :=:=:=:=:=:=: Starting to sample for next [" + training_or_validation_str + "]... :=:=:=:=:=:=:")
    
    total_number_of_subjects = len(paths_per_chan_per_subj)
    inds_of_subjects_for_subep = get_random_subjects_to_train_subep( total_number_of_subjects = total_number_of_subjects,
                                                                     max_subjects_on_gpu_for_subepoch = max_n_cases_per_subep,
                                                                     get_max_subjects_for_gpu_even_if_total_less = False )
    log.print3(id_str+" Out of [" + str(total_number_of_subjects) + "] subjects given for [" + training_or_validation_str + "], "+
               "we will sample from maximum [" + str(max_n_cases_per_subep) + "] per subepoch.")
    log.print3(id_str+" Shuffled indices of subjects that were randomly chosen: "+str(inds_of_subjects_for_subep))
    
    # List, with [numberOfPathwaysThatTakeInput] sublists. Each sublist is list of [partImagesLoadedPerSubepoch] arrays [channels, R,C,Z].
    channelsOfSegmentsForSubepochListPerPathway = [ [] for i in range(cnn3d.getNumPathwaysThatRequireInput()) ]
    lblsForPredictedPartOfSegmentsForSubepochList = [] # Labels only for the central/predicted part of segments.
    n_subjects_for_subep = len(inds_of_subjects_for_subep) #Can be different than max_n_cases_per_subep, cause of available images number.
    
    # This is to separate each sampling category (fore/background, uniform, full-image, weighted-classes)
    n_samples_per_cat_per_subj = get_num_samples_per_cat_per_subj(n_samples_per_subep,
                                                                  sampling_type.getPercentOfSamplesPerCategoryToSample(),
                                                                  n_subjects_for_subep )
    
    args_sampling_job = [log,
                        train_or_val,
                        run_input_checks,
                        cnn3d,
                        sampling_type,
                        paths_per_chan_per_subj,
                        paths_to_lbls_per_subj,
                        provided_mask,
                        paths_to_masks_per_subj,
                        provided_weightmaps_per_sampl_cat,
                        paths_to_wmaps_per_sampl_cat_per_subj,
                        # Pre-processing:
                        pad_input_imgs,
                        augm_params,
                        
                        n_subjects_for_subep,
                        inds_of_subjects_for_subep,
                        n_samples_per_cat_per_subj ]
    
    log.print3(id_str+" Will sample from [" + str(n_subjects_for_subep) + "] subjects for next " + training_or_validation_str + "...")
    
    jobs_inds_to_do = list(range(n_subjects_for_subep)) # One job per subject.
    
    if num_parallel_proc <= 0: # Sequentially
        for job_i in jobs_inds_to_do :
            (channelsOfSegmentsFromThisSubjPerPathway,
            lblsOfPredictedPartOfSegmentsFromThisSubj) = load_subj_and_get_samples( *( [job_i]+args_sampling_job ) )
            for pathway_i in range(cnn3d.getNumPathwaysThatRequireInput()) :
                channelsOfSegmentsForSubepochListPerPathway[pathway_i] += channelsOfSegmentsFromThisSubjPerPathway[pathway_i] # concat does not copy.
            lblsForPredictedPartOfSegmentsForSubepochList += lblsOfPredictedPartOfSegmentsFromThisSubj # concat does not copy.

    else: # Parallelize sampling from each subject
        while len(jobs_inds_to_do) > 0: # While jobs remain.
            jobs = collections.OrderedDict()
            
            log.print3(id_str+" ******* Spawning children processes to sample from [" + str(len(jobs_inds_to_do)) + "] subjects*******")
            log.print3(id_str+" MULTIPROC: Number of CPUs detected: " + str(multiprocessing.cpu_count()) + ". Requested to use max: [" + str(num_parallel_proc) + "]")
            num_workers = min(num_parallel_proc, multiprocessing.cpu_count())
            log.print3(id_str+" MULTIPROC: Spawning [" + str(num_workers) + "] processes to load data and sample.")
            worker_pool = multiprocessing.Pool(processes=num_workers, initializer=init_sampling_proc) 

            try: # Stacktrace in multiprocessing: https://jichu4n.com/posts/python-multiprocessing-and-exceptions/
                for job_i in jobs_inds_to_do: # submit jobs
                    jobs[job_i] = worker_pool.apply_async( load_subj_and_get_samples, ( [job_i]+args_sampling_job ) )
                
                for job_i in list(jobs_inds_to_do): # copy with list(...), so that this loops normally even if something is removed from list.
                    try:
                        (channelsOfSegmentsFromThisSubjPerPathway,
                        lblsOfPredictedPartOfSegmentsFromThisSubj) = jobs[job_i].get(timeout=10) # timeout in case process for some reason never started (happens in py3)
                        for pathway_i in range(cnn3d.getNumPathwaysThatRequireInput()) :
                            channelsOfSegmentsForSubepochListPerPathway[pathway_i] += channelsOfSegmentsFromThisSubjPerPathway[pathway_i] # concat does not copy.
                        lblsForPredictedPartOfSegmentsForSubepochList += lblsOfPredictedPartOfSegmentsFromThisSubj # concat does not copy.
                        jobs_inds_to_do.remove(job_i)
                    except multiprocessing.TimeoutError as e:
                        log.print3(id_str+"\n\n WARN: MULTIPROC: Caught TimeoutError when getting results of job [" + str(job_i) + "].\n" +
                                   " WARN: MULTIPROC: Will resubmit job [" + str(job_i) + "].\n")
                        if num_workers == 1:
                            break # If this 1 worker got stuck, every job will wait timeout. Slow. Recreate pool.
            
            except (Exception, KeyboardInterrupt) as e:
                log.print3(id_str+"\n\n ERROR: Caught exception in getSampledDataAndLabelsForSubepoch(): "+str(e)+"\n")
                log.print3( traceback.format_exc() )
                worker_pool.terminate()
                worker_pool.join() # Will wait. A KeybInt will kill this (py3)
                raise e
            except: # Catches everything, even a sys.exit(1) exception.
                log.print3(id_str+"\n\n ERROR: Unexpected error in getSampledDataAndLabelsForSubepoch(). System info: ", sys.exc_info()[0])
                worker_pool.terminate()
                worker_pool.join()
                raise Exception("Unexpected error.")
            else: # Nothing went wrong
                worker_pool.terminate() # # Needed in case any processes are hunging. worker_pool.close() does not solve this.
                worker_pool.join()
               
    # Got all samples for subepoch. Now shuffle them, together segments and their labels.
    [channelsOfSegmentsForSubepochListPerPathway,
    lblsForPredictedPartOfSegmentsForSubepochList ] = shuffleSegmentsOfThisSubepoch(channelsOfSegmentsForSubepochListPerPathway,
                                                                                    lblsForPredictedPartOfSegmentsForSubepochList )
    end_time_sampling = time.time()
    log.print3(id_str+" TIMING: Sampling for next [" + training_or_validation_str + "] lasted: {0:.1f}".format(end_time_sampling-start_time_sampling)+" secs.")
    
    log.print3(id_str+" :=:=:=:=:=:=: Finished sampling for next [" + training_or_validation_str + "] :=:=:=:=:=:=:")
    
    channelsOfSegmentsForSubepochArrayPerPathway = [ np.asarray(imPartsForPathwayi, dtype="float32") for imPartsForPathwayi in channelsOfSegmentsForSubepochListPerPathway ]
    lblsForPredictedPartOfSegmentsForSubepochArray = np.asarray(lblsForPredictedPartOfSegmentsForSubepochList, dtype="int32") # Could be int16 to save RAM?
    
    return [channelsOfSegmentsForSubepochArrayPerPathway,
            lblsForPredictedPartOfSegmentsForSubepochArray]
    
    
    
def init_sampling_proc():
    # This will make child-processes ignore the KeyboardInterupt (sigInt). Parent will handle it.
    # See: http://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python/35134329#35134329 
    signal.signal(signal.SIGINT, signal.SIG_IGN) 


    
def get_random_subjects_to_train_subep( total_number_of_subjects, 
                                        max_subjects_on_gpu_for_subepoch, 
                                        get_max_subjects_for_gpu_even_if_total_less=False ):
    # Returns: list of indices
    subjects_indices = list(range(total_number_of_subjects)) #list() for python3 compatibility, as range cannot get assignment in shuffle()
    random_order_chosen_subjects=[]
    random.shuffle(subjects_indices) #does it in place. Now they are shuffled
    
    if max_subjects_on_gpu_for_subepoch>=total_number_of_subjects:
        random_order_chosen_subjects += subjects_indices
        
        if get_max_subjects_for_gpu_even_if_total_less : #This is if I want to have a certain amount on GPU, even if total subjects are less.
            while (len(random_order_chosen_subjects)<max_subjects_on_gpu_for_subepoch):
                random.shuffle(subjects_indices)
                number_of_extra_subjects_to_get_to_fill_gpu = min(max_subjects_on_gpu_for_subepoch - len(random_order_chosen_subjects), total_number_of_subjects)
                random_order_chosen_subjects += (subjects_indices[:number_of_extra_subjects_to_get_to_fill_gpu])
            assert len(random_order_chosen_subjects) != max_subjects_on_gpu_for_subepoch
    else:
        random_order_chosen_subjects += subjects_indices[:max_subjects_on_gpu_for_subepoch]
        
    return random_order_chosen_subjects



def get_num_samples_per_cat_per_subj(n_samples_per_subep,
                                     perc_samples_per_cat,
                                     n_subjects_for_subep ) :
    # perc_samples_per_cat: list with a percentage for each type of category to sample.
    
    # First, distribute n_samples_per_subep to the categories:
    n_sampl_categs = len(perc_samples_per_cat)
    n_samples_per_cat = np.zeros( n_sampl_categs, dtype="int32" )
    for cat_i in range(n_sampl_categs) :
        n_samples_per_cat[cat_i] += int(n_samples_per_subep * perc_samples_per_cat[cat_i])
    # Distribute samples that were left if perc dont exactly add to 1.
    n_undistributed_samples = n_samples_per_subep - np.sum(n_samples_per_cat)
    cats_to_distribute_samples = np.random.choice(n_sampl_categs, size=n_undistributed_samples, replace=True, p=perc_samples_per_cat)
    for cat_i in cats_to_distribute_samples :
        n_samples_per_cat[cat_i] += 1
    
    # Distribute samples of each cat to subjects.
    n_samples_per_cat_per_subj = np.zeros( [ n_sampl_categs, n_subjects_for_subep ] , dtype="int32" )
    for cat_i in range(n_sampl_categs) :
        n_samples_per_cat_per_subj[cat_i] += n_samples_per_cat[cat_i] // n_subjects_for_subep
        n_undistributed_samples_in_cat = n_samples_per_cat[cat_i] % n_subjects_for_subep
        for idx in range(n_undistributed_samples_in_cat):
            n_samples_per_cat_per_subj[cat_i, random.randint(0, n_subjects_for_subep - 1)] += 1
            
    return n_samples_per_cat_per_subj
    
    
    
def load_subj_and_get_samples(job_i,
                              log,
                              train_or_val,
                              run_input_checks,
                              cnn3d,
                              sampling_type,
                              paths_per_chan_per_subj,
                              paths_to_lbls_per_subj,
                              provided_mask,
                              paths_to_masks_per_subj,
                              provided_weightmaps_per_sampl_cat,
                              paths_to_wmaps_per_sampl_cat_per_subj,
                              # Pre-processing:
                              pad_input_imgs,
                              augm_params,
                              
                              n_subjects_for_subep,
                              inds_of_subjects_for_subep,
                              n_samples_per_cat_per_subj
                              ):
    # paths_per_chan_per_subj: [ [ for channel-0 [ one path per subj ] ], ..., [ for channel-n  [ one path per subj ] ] ]
    # n_samples_per_cat_per_subj: np arr, shape [num sampling categories, num subjects in subepoch]
    # returns: ( channelsOfSegmentsFromThisSubjPerPathway, lblsOfPredictedPartOfSegmentsFromThisSubj )
    id_str = "[JOB:"+str(job_i)+"|PID:"+str(os.getpid())+"]"
    log.print3(id_str+" Load & sample from subject of index (in user's list): " + str(inds_of_subjects_for_subep[job_i]) +\
               " (Job #" + str(job_i) + "/" +str(n_subjects_for_subep)+")")
    
    # List, with [numberOfPathwaysThatTakeInput] sublists. Each sublist is list of [partImagesLoadedPerSubepoch] arrays [channels, R,C,Z].
    channelsOfSegmentsFromThisSubjPerPathway = [ [] for i in range(cnn3d.getNumPathwaysThatRequireInput()) ]
    lblsOfPredictedPartOfSegmentsFromThisSubj = [] # Labels only for the central/predicted part of segments.
    
    dimsOfPrimeSegmentRcz = cnn3d.pathways[0].getShapeOfInput(train_or_val)[2:]
    
    [allChannelsOfPatientInNpArray, # nparray(channels,dim0,dim1,dim2)
    gtLabelsImage,
    roiMask,
    arrayWithWeightMapsWhereToSampleForEachCategory,
    tupleOfPaddingPerAxesLeftRight #( (padLeftR, padRightR), (padLeftC,padRightC), (padLeftZ,padRightZ)). All 0s when no padding.
    ] = load_imgs_of_subject(log,
                             job_i,
                             train_or_val,
                             run_input_checks,
                             inds_of_subjects_for_subep[job_i],
                             paths_per_chan_per_subj,
                             True, # providedGtLabelsBool. If this getTheArr function is called (training), gtLabels should already been provided.
                             paths_to_lbls_per_subj, 
                             cnn3d.num_classes,
                             provided_weightmaps_per_sampl_cat, # If true, must provide all. Placeholder in testing.
                             paths_to_wmaps_per_sampl_cat_per_subj, # Placeholder in testing.
                             provided_mask,
                             paths_to_masks_per_subj,
                             # Preprocessing
                             pad_input_imgs,
                             cnn3d.recFieldCnn, # used if pad_input_imgs
                             dimsOfPrimeSegmentRcz) # used if pad_input_imgs
    
    dimensionsOfImageChannel = allChannelsOfPatientInNpArray[0].shape
    finalWeightMapsToSampleFromPerCategoryForSubject = sampling_type.logicDecidingAndGivingFinalSamplingMapsForEachCategory(
                                                                                            provided_weightmaps_per_sampl_cat,
                                                                                            arrayWithWeightMapsWhereToSampleForEachCategory,
                                                                                            True, #providedGtLabelsBool. True both for train and val.
                                                                                            gtLabelsImage,
                                                                                            provided_mask,
                                                                                            roiMask,
                                                                                            dimensionsOfImageChannel)
    str_samples_per_cat = " Got samples per category: "
    for cat_i in range( sampling_type.getNumberOfCategoriesToSample() ) :
        catString = sampling_type.getStringsPerCategoryToSample()[cat_i]
        numOfSegmsToExtractForThisCatFromThisSubject = n_samples_per_cat_per_subj[cat_i][job_i]
        finalWeightMapToSampleFromForThisCat = finalWeightMapsToSampleFromPerCategoryForSubject[cat_i]
        
        # Check if the weight map is fully-zeros. In this case, don't call the sampling function, just continue.
        # Note that this way, the data loaded on GPU will not be as much as I initially wanted. Thus calculate number-of-batches from this actual number of extracted segments.
        if np.sum(finalWeightMapToSampleFromForThisCat>0) == 0 :
            log.print3(id_str+" WARN: Sampling mask/map was found just zeros! No [" + catString + "] samples for this subject!")
            continue
        
        coords_of_samples = sample_coords_of_segments(log,
                                            job_i,
                                            numOfSegmsToExtractForThisCatFromThisSubject,
                                            dimsOfPrimeSegmentRcz,
                                            dimensionsOfImageChannel,
                                            finalWeightMapToSampleFromForThisCat)
        str_samples_per_cat += "[" + catString + ": " + str(len(coords_of_samples[0][0])) + "/" + str(numOfSegmsToExtractForThisCatFromThisSubject) + "] "
        
        # Use the just sampled coordinates of slices to actually extract the segments (data) from the subject's images. 
        for image_part_i in range(len(coords_of_samples[0][0])) :
            coordsOfCentralVoxelOfThisImPart = coords_of_samples[0][:,image_part_i]
            
            [channelsForSegmentPerPathway,
            lblsOfPredictedPartOfSegment # used to be gtLabelsForThisImagePart, before extracting only for the central voxels.
            ] = extractSegmentGivenSliceCoords(train_or_val,
                                               cnn3d,
                                               coordsOfCentralVoxelOfThisImPart,
                                               allChannelsOfPatientInNpArray,
                                               gtLabelsImage)
            
            # Augmentation of segments
            channelsForSegmentPerPathway, lblsOfPredictedPartOfSegment = augment_patch(channelsForSegmentPerPathway, lblsOfPredictedPartOfSegment, augm_params)
            
            for pathway_i in range(cnn3d.getNumPathwaysThatRequireInput()) :
                channelsOfSegmentsFromThisSubjPerPathway[pathway_i].append(channelsForSegmentPerPathway[pathway_i])
            lblsOfPredictedPartOfSegmentsFromThisSubj.append(lblsOfPredictedPartOfSegment)
    
    log.print3(id_str + str_samples_per_cat)
    return (channelsOfSegmentsFromThisSubjPerPathway, lblsOfPredictedPartOfSegmentsFromThisSubj)



# roi_mask_filename and roiMinusLesion_mask_filename can be passed "no". In this case, the corresponding return result is nothing.
# This is so because: the do_training() function only needs the roiMinusLesion_mask, whereas the do_testing() only needs the roi_mask.        
def load_imgs_of_subject(log,
                         job_i, # None in testing.
                         train_val_or_test,
                         run_input_checks,
                         subj_i,
                         paths_per_chan_per_subj,
                         providedGtLabelsBool,
                         listOfFilepathsToGtLabelsOfEachPatient,
                         num_classes,
                         provided_weightmaps_per_sampl_cat, # If true, must provide all wmaps. Placeholder in testing.
                         paths_to_wmaps_per_sampl_cat_per_subj, # Placeholder in testing.
                         provided_mask,
                         paths_to_masks_per_subj,
                         # Preprocessing
                         pad_input_imgs,
                         cnnReceptiveField, # only used if pad_input_imgs
                         dimsOfPrimeSegmentRcz
                         ):
    #listOfNiiFilepathNames: should be a list of lists. Each sublist corresponds to one certain subject.
    #...Each sublist should have as many elements(strings-filenamePaths) as numberOfChannels, point to the channels of this patient.
    id_str = "[JOB:"+str(job_i)+"|PID:"+str(os.getpid())+"] " if job_i is not None else "" # is None in testing.
    
    if subj_i >= len(paths_per_chan_per_subj) :
        raise ValueError(id_str+" The argument 'subj_i' given is greater than the filenames given for the .nii folders!")
    
    log.print3(id_str+"Loading subject with 1st channel at: "+str(paths_per_chan_per_subj[subj_i][0]))
    
    numberOfNormalScaleChannels = len(paths_per_chan_per_subj[0])

    tupleOfPaddingPerAxesLeftRight = ((0,0), (0,0), (0,0)) #This will be given a proper value if padding is performed.
    
    if provided_mask :
        fullFilenamePathOfRoiMask = paths_to_masks_per_subj[subj_i]
        roiMask = loadVolume(fullFilenamePathOfRoiMask)
        
        [roiMask, tupleOfPaddingPerAxesLeftRight] = padCnnInputs(roiMask, cnnReceptiveField, dimsOfPrimeSegmentRcz) if pad_input_imgs else [roiMask, tupleOfPaddingPerAxesLeftRight]
    else :
        roiMask = None
        
    #Load the channels of the patient.
    niiDimensions = None
    allChannelsOfPatientInNpArray = None
    #The below has dimensions (channels, 2). Holds per channel: [value to add per voxel for mean norm, value to multiply for std renorm]
    howMuchToAddAndMultiplyForNormalizationAugmentationForEachChannel = np.ones( (numberOfNormalScaleChannels, 2), dtype="float32")
    for channel_i in range(numberOfNormalScaleChannels):
        fullFilenamePathOfChannel = paths_per_chan_per_subj[subj_i][channel_i]
        if fullFilenamePathOfChannel != "-" : #normal case, filepath was given.
            channelData = loadVolume(fullFilenamePathOfChannel)
                
            [channelData, tupleOfPaddingPerAxesLeftRight] = padCnnInputs(channelData, cnnReceptiveField, dimsOfPrimeSegmentRcz) if pad_input_imgs else [channelData, tupleOfPaddingPerAxesLeftRight]
            
            if not isinstance(allChannelsOfPatientInNpArray, (np.ndarray)) :
                #Initialize the array in which all the channels for the patient will be placed.
                niiDimensions = list(channelData.shape)
                allChannelsOfPatientInNpArray = np.zeros( (numberOfNormalScaleChannels, niiDimensions[0], niiDimensions[1], niiDimensions[2]))
                
            allChannelsOfPatientInNpArray[channel_i] = channelData
        else : # "-" was given in the config-listing file. Do Min-fill!
            log.print3(id_str+" WARN: No modality #"+str(channel_i)+" given. Will make input channel full of zeros.")
            allChannelsOfPatientInNpArray[channel_i] = -4.0
            
        
    #Load the class labels.
    if providedGtLabelsBool : #For training (exact target labels) or validation on samples labels.
        fullFilenamePathOfGtLabels = listOfFilepathsToGtLabelsOfEachPatient[subj_i]
        imageGtLabels = loadVolume(fullFilenamePathOfGtLabels)
        
        if imageGtLabels.dtype.kind not in ['i','u']:
            log.print3(id_str+" WARN: Loaded labels are dtype ["+str(imageGtLabels.dtype)+"]. Rounding and casting them to int!")
            imageGtLabels = np.rint(imageGtLabels).astype("int32")
            
        if run_input_checks:
            check_gt_vs_num_classes(log, imageGtLabels, num_classes)

        [imageGtLabels, tupleOfPaddingPerAxesLeftRight] = padCnnInputs(imageGtLabels, cnnReceptiveField, dimsOfPrimeSegmentRcz) if pad_input_imgs else [imageGtLabels, tupleOfPaddingPerAxesLeftRight]
    else : 
        imageGtLabels = None #For validation and testing
        
    if train_val_or_test != "test" and provided_weightmaps_per_sampl_cat==True : # in testing these weightedMaps are never provided, they are for training/validation only.
        n_sampl_categs = len(paths_to_wmaps_per_sampl_cat_per_subj)
        arrayWithWeightMapsWhereToSampleForEachCategory = np.zeros( [n_sampl_categs] + list(allChannelsOfPatientInNpArray[0].shape), dtype="float32" ) 
        for cat_i in range( n_sampl_categs ) :
            filepathsToTheWeightMapsOfAllPatientsForThisCategory = paths_to_wmaps_per_sampl_cat_per_subj[cat_i]
            filepathToTheWeightMapOfThisPatientForThisCategory = filepathsToTheWeightMapsOfAllPatientsForThisCategory[subj_i]
            weightedMapForThisCatData = loadVolume(filepathToTheWeightMapOfThisPatientForThisCategory)
            
            [weightedMapForThisCatData, tupleOfPaddingPerAxesLeftRight] = padCnnInputs(weightedMapForThisCatData, cnnReceptiveField, dimsOfPrimeSegmentRcz) if pad_input_imgs else [weightedMapForThisCatData, tupleOfPaddingPerAxesLeftRight]
            
            arrayWithWeightMapsWhereToSampleForEachCategory[cat_i] = weightedMapForThisCatData
    else :
        arrayWithWeightMapsWhereToSampleForEachCategory = None
    
    return [allChannelsOfPatientInNpArray, imageGtLabels, roiMask, arrayWithWeightMapsWhereToSampleForEachCategory, tupleOfPaddingPerAxesLeftRight]



#made for 3d
def sample_coords_of_segments(  log,
                                job_i,
                                numOfSegmentsToExtractForThisSubject,
                                dimsOfSegmentRcz,
                                dimensionsOfImageChannel,
                                weightMapToSampleFrom ) :
    """
    This function returns the coordinates (index) of the "central" voxel of sampled image parts (1voxel to the left if even part-dimension).
    It also returns the indices of the image parts, left and right indices, INCLUSIVE BOTH SIDES.
    
    Return value: [ rcz-coordsOfCentralVoxelsOfPartsSampled, rcz-sliceCoordsOfImagePartsSampled ]
    > coordsOfCentralVoxelsOfPartsSampled : an array with shape: 3(rcz) x numOfSegmentsToExtractForThisSubject. 
        Example: [ rCoordsForCentralVoxelOfEachPart, cCoordsForCentralVoxelOfEachPart, zCoordsForCentralVoxelOfEachPart ]
        >> r/c/z-CoordsForCentralVoxelOfEachPart : A 1-dim array with numOfSegmentsToExtractForThisSubject, that holds the r-index within the image of each sampled part.
    > sliceCoordsOfImagePartsSampled : 3(rcz) x NumberOfImagePartSamples x 2. The last dimension has [0] for the lower boundary of the slice, and [1] for the higher boundary. INCLUSIVE BOTH SIDES.
        Example: [ r-sliceCoordsOfImagePart, c-sliceCoordsOfImagePart, z-sliceCoordsOfImagePart ]
    """
    id_str = "[JOB:"+str(job_i)+"|PID:"+str(os.getpid())+"]"
    # Check if the weight map is fully-zeros. In this case, return no element.
    # Note: Currently, the caller function is checking this case already and does not let this being called. Which is still fine.
    if np.sum(weightMapToSampleFrom>0) == 0 :
        log.print3(id_str+" WARN: The sampling mask/map was found just zeros! No image parts were sampled for this subject!")
        return [ [[],[],[]], [[],[],[]] ]
    
    imagePartsSampled = []
    
    #Now out of these, I need to randomly select one, which will be an ImagePart's central voxel.
    #But I need to be CAREFUL and get one that IS NOT closer to the image boundaries than the dimensions of the ImagePart permit.
    
    #I look for lesions that are not closer to the image boundaries than the ImagePart dimensions allow.
    #KernelDim is always odd. BUT ImagePart dimensions can be odd or even.
    #If odd, ok, floor(dim/2) from central.
    #If even, dim/2-1 voxels towards the begining of the axis and dim/2 towards the end. Ie, "central" imagePart voxel is 1 closer to begining.
    #BTW imagePartDim takes kernel into account (ie if I want 9^3 voxels classified per imagePart with kernel 5x5, I want 13 dim ImagePart)
    
    halfImagePartBoundaries = np.zeros( (len(dimsOfSegmentRcz), 2) , dtype='int32') #dim1: 1 row per r,c,z. Dim2: left/right width not to sample from (=half segment).
    
    #The below starts all zero. Will be Multiplied by other true-false arrays expressing if the relevant voxels are within boundaries.
    #In the end, the final vector will be true only for the indices of lesions that are within all boundaries.
    booleanNpArray_voxelsToCentraliseImPartsWithinBoundaries = np.zeros(weightMapToSampleFrom.shape, dtype="int32")
    
    # This loop leads to booleanNpArray_voxelsToCentraliseImPartsWithinBoundaries to be true for the indices ...
    # ...that allow getting an imagePart CENTERED on them, and be safely within image boundaries. Note that ...
    # ... if the imagePart is of even dimension, the "central" voxel is one voxel to the left.
    for rcz_i in range( len(dimsOfSegmentRcz) ) :
        if dimsOfSegmentRcz[rcz_i]%2 == 0: #even
            dimensionDividedByTwo = dimsOfSegmentRcz[rcz_i]//2
            halfImagePartBoundaries[rcz_i] = [dimensionDividedByTwo - 1, dimensionDividedByTwo] #central of ImagePart is 1 vox closer to begining of axes.
        else: #odd
            dimensionDividedByTwoFloor = math.floor(dimsOfSegmentRcz[rcz_i]//2) #eg 5/2 = 2, with the 3rd voxel being the "central"
            halfImagePartBoundaries[rcz_i] = [dimensionDividedByTwoFloor, dimensionDividedByTwoFloor] 
    #used to be [halfImagePartBoundaries[0][0]: -halfImagePartBoundaries[0][1]], but in 2D case halfImagePartBoundaries might be ==0, causes problem and you get a null slice.
    booleanNpArray_voxelsToCentraliseImPartsWithinBoundaries[halfImagePartBoundaries[0][0]: dimensionsOfImageChannel[0] - halfImagePartBoundaries[0][1],
                                                            halfImagePartBoundaries[1][0]: dimensionsOfImageChannel[1] - halfImagePartBoundaries[1][1],
                                                            halfImagePartBoundaries[2][0]: dimensionsOfImageChannel[2] - halfImagePartBoundaries[2][1]] = 1
                                                            
    constrainedWithImageBoundariesMaskToSample = weightMapToSampleFrom * booleanNpArray_voxelsToCentraliseImPartsWithinBoundaries
    #normalize the probabilities to sum to 1, cause the function needs it as so.
    constrainedWithImageBoundariesMaskToSample = constrainedWithImageBoundariesMaskToSample / (1.0* np.sum(constrainedWithImageBoundariesMaskToSample))
    
    flattenedConstrainedWithImageBoundariesMaskToSample = constrainedWithImageBoundariesMaskToSample.flatten()
    
    #This is going to be a 3xNumberOfImagePartSamples array.
    indicesInTheFlattenArrayThatWereSampledAsCentralVoxelsOfImageParts = np.random.choice(  constrainedWithImageBoundariesMaskToSample.size,
                                                                                            size = numOfSegmentsToExtractForThisSubject,
                                                                                            replace=True,
                                                                                            p=flattenedConstrainedWithImageBoundariesMaskToSample)
    # np.unravel_index([listOfIndicesInFlattened], dims) returns a tuple of arrays (eg 3 of them if 3 dimImage), 
    # where each of the array in the tuple has the same shape as the listOfIndices. 
    # They have the r/c/z coords that correspond to the index of the flattened version.
    # So, coordsOfCentralVoxelsOfPartsSampled will be array of shape: 3(rcz) x numOfSegmentsToExtractForThisSubject.
    coordsOfCentralVoxelsOfPartsSampled = np.asarray(np.unravel_index(indicesInTheFlattenArrayThatWereSampledAsCentralVoxelsOfImageParts,
                                                                    constrainedWithImageBoundariesMaskToSample.shape #the shape of the roiMask/scan.
                                                                    )
                                                    )
    # Array with shape: 3(rcz) x NumberOfImagePartSamples x 2.
    # Last dimension has [0] for lowest boundary of slice, and [1] for highest boundary. INCLUSIVE BOTH SIDES.
    sliceCoordsOfImagePartsSampled = np.zeros(list(coordsOfCentralVoxelsOfPartsSampled.shape) + [2], dtype="int32")
    sliceCoordsOfImagePartsSampled[:,:,0] = coordsOfCentralVoxelsOfPartsSampled - halfImagePartBoundaries[ :, np.newaxis, 0 ] #np.newaxis broadcasts. To broadcast the -+.
    sliceCoordsOfImagePartsSampled[:,:,1] = coordsOfCentralVoxelsOfPartsSampled + halfImagePartBoundaries[ :, np.newaxis, 1 ]
    
    # coordsOfCentralVoxelsOfPartsSampled: Array of dimensions 3(rcz) x NumberOfImagePartSamples.
    # sliceCoordsOfImagePartsSampled: Array of dimensions 3(rcz) x NumberOfImagePartSamples x 2. ...
    # ... The last dim has [0] for the lower boundary of the slice, and [1] for the higher boundary.
    # ... The slice coordinates returned are INCLUSIVE BOTH sides.
    imagePartsSampled = [coordsOfCentralVoxelsOfPartsSampled, sliceCoordsOfImagePartsSampled]
    return imagePartsSampled



def getImagePartFromSubsampledImageForTraining( dimsOfPrimarySegment,
                                                recFieldCnn,
                                                subsampledImageChannels,
                                                image_part_slices_coords,
                                                subSamplingFactor,
                                                subsampledImagePartDimensions
                                                ) :
    """
    This returns an image part from the sampled data, given the image_part_slices_coords,
    which has the coordinates where the normal-scale image part starts and ends (inclusive).
    (Actually, in this case, the right (end) part of image_part_slices_coords is not used.)
    
    The way it works is NOT optimal. From the beginning of the normal-resolution part,
    it goes further to the left 1 receptive-field and then forward xSubsamplingFactor receptive-fields.
    This stops it from being used with arbitrary size of subsampled segment (decoupled by the high-res segment).
    Now, the subsampled patch has to be of the same size as the normal-scale.
    To change this, I should find where THE FIRST TOP LEFT CENTRAL (predicted) VOXEL is, 
    and do the back-one-(sub)patch + front-3-(sub)patches from there, not from the begining of the patch.
    
    Current way it works (correct):
    If I have eg subsample factor=3 and 9 central-pred-voxels, I get 3 "central" voxels/patches for the
    subsampled-part. Straightforward. If I have a number of central voxels that is not an exact multiple of
    the subfactor, eg 10 central-voxels, I get 3+1 central voxels in the subsampled-part. 
    When the cnn is convolving them, they will get repeated to 4(last-layer-neurons)*3(factor) = 12, 
    and will get sliced down to 10, in order to have same dimension with the 1st pathway.
    """
    subsampledImageDimensions = subsampledImageChannels[0].shape
    
    subsampledChannelsForThisImagePart = np.ones((len(subsampledImageChannels),
                                                  subsampledImagePartDimensions[0],
                                                  subsampledImagePartDimensions[1],
                                                  subsampledImagePartDimensions[2]),
                                                 dtype = 'float32')
    
    numberOfCentralVoxelsClassifiedForEachImagePart_rDim = dimsOfPrimarySegment[0] - recFieldCnn[0] + 1
    numberOfCentralVoxelsClassifiedForEachImagePart_cDim = dimsOfPrimarySegment[1] - recFieldCnn[1] + 1
    numberOfCentralVoxelsClassifiedForEachImagePart_zDim = dimsOfPrimarySegment[2] - recFieldCnn[2] + 1
    
    #Calculate the slice that I should get, and where I should put it in the imagePart (eg if near the borders, and I cant grab a whole slice-imagePart).
    rSlotsPreviously = ((subSamplingFactor[0]-1)//2)*recFieldCnn[0] if subSamplingFactor[0]%2==1 \
                                                else (subSamplingFactor[0]-2)//2*recFieldCnn[0] + recFieldCnn[0]//2
    cSlotsPreviously = ((subSamplingFactor[1]-1)//2)*recFieldCnn[1] if subSamplingFactor[1]%2==1 \
                                                else (subSamplingFactor[1]-2)//2*recFieldCnn[1] + recFieldCnn[1]//2
    zSlotsPreviously = ((subSamplingFactor[2]-1)//2)*recFieldCnn[2] if subSamplingFactor[2]%2==1 \
                                                else (subSamplingFactor[2]-2)//2*recFieldCnn[2] + recFieldCnn[2]//2
    #1*17
    rToCentralVoxelOfAnAveragedArea = subSamplingFactor[0]//2 if subSamplingFactor[0]%2==1 else (subSamplingFactor[0]//2 - 1) #one closer to the beginning of dim. Same happens when I get parts of image.
    cToCentralVoxelOfAnAveragedArea = subSamplingFactor[1]//2 if subSamplingFactor[1]%2==1 else (subSamplingFactor[1]//2 - 1)
    zToCentralVoxelOfAnAveragedArea =  subSamplingFactor[2]//2 if subSamplingFactor[2]%2==1 else (subSamplingFactor[2]//2 - 1)
    #This is where to start taking voxels from the subsampled image. From the beginning of the imagePart(1 st patch)...
    #... go forward a few steps to the voxel that is like the "central" in this subsampled (eg 3x3) area. 
    #...Then go backwards -Patchsize to find the first voxel of the subsampled. 
    rlow = image_part_slices_coords[0][0] + rToCentralVoxelOfAnAveragedArea - rSlotsPreviously#These indices can run out of image boundaries. I ll correct them afterwards.
    #If the patch is 17x17, I want a 17x17 subsampled Patch. BUT if the imgPART is 25x25 (9voxClass), I want 3 subsampledPatches in my subsampPart to cover this area!
    #That is what the last term below is taking care of.
    #CAST TO INT because ceil returns a float, and later on when computing rHighNonInclToPutTheNotPaddedInSubsampledImPart I need to do INTEGER DIVISION.
    rhighNonIncl = int(rlow + subSamplingFactor[0]*recFieldCnn[0] + (math.ceil((numberOfCentralVoxelsClassifiedForEachImagePart_rDim*1.0)/subSamplingFactor[0]) - 1) * subSamplingFactor[0]) # excluding index in segment
    clow = image_part_slices_coords[1][0] + cToCentralVoxelOfAnAveragedArea - cSlotsPreviously
    chighNonIncl = int(clow + subSamplingFactor[1]*recFieldCnn[1] + (math.ceil((numberOfCentralVoxelsClassifiedForEachImagePart_cDim*1.0)/subSamplingFactor[1]) - 1) * subSamplingFactor[1])
    zlow = image_part_slices_coords[2][0] + zToCentralVoxelOfAnAveragedArea - zSlotsPreviously
    zhighNonIncl = int(zlow + subSamplingFactor[2]*recFieldCnn[2] + (math.ceil((numberOfCentralVoxelsClassifiedForEachImagePart_zDim*1.0)/subSamplingFactor[2]) - 1) * subSamplingFactor[2])
        
    rlowCorrected = max(rlow, 0)
    clowCorrected = max(clow, 0)
    zlowCorrected = max(zlow, 0)
    rhighNonInclCorrected = min(rhighNonIncl, subsampledImageDimensions[0])
    chighNonInclCorrected = min(chighNonIncl, subsampledImageDimensions[1])
    zhighNonInclCorrected = min(zhighNonIncl, subsampledImageDimensions[2]) #This gave 7
    
    rLowToPutTheNotPaddedInSubsampledImPart = 0 if rlow >= 0 else abs(rlow)//subSamplingFactor[0]
    cLowToPutTheNotPaddedInSubsampledImPart = 0 if clow >= 0 else abs(clow)//subSamplingFactor[1]
    zLowToPutTheNotPaddedInSubsampledImPart = 0 if zlow >= 0 else abs(zlow)//subSamplingFactor[2]
    
    dimensionsOfTheSliceOfSubsampledImageNotPadded = [  int(math.ceil((rhighNonInclCorrected - rlowCorrected)*1.0/subSamplingFactor[0])),
                                                        int(math.ceil((chighNonInclCorrected - clowCorrected)*1.0/subSamplingFactor[1])),
                                                        int(math.ceil((zhighNonInclCorrected - zlowCorrected)*1.0/subSamplingFactor[2]))
                                                        ]
    
    #I now have exactly where to get the slice from and where to put it in the new array.
    for channel_i in range(len(subsampledImageChannels)) :
        intensityZeroOfChannel = calculateTheZeroIntensityOf3dImage(subsampledImageChannels[channel_i])        
        subsampledChannelsForThisImagePart[channel_i] *= intensityZeroOfChannel
        
        sliceOfSubsampledImageNotPadded = subsampledImageChannels[channel_i][   rlowCorrected : rhighNonInclCorrected : subSamplingFactor[0],
                                                                                clowCorrected : chighNonInclCorrected : subSamplingFactor[1],
                                                                                zlowCorrected : zhighNonInclCorrected : subSamplingFactor[2]
                                                                            ]
        subsampledChannelsForThisImagePart[
            channel_i,
            rLowToPutTheNotPaddedInSubsampledImPart : rLowToPutTheNotPaddedInSubsampledImPart+dimensionsOfTheSliceOfSubsampledImageNotPadded[0],
            cLowToPutTheNotPaddedInSubsampledImPart : cLowToPutTheNotPaddedInSubsampledImPart+dimensionsOfTheSliceOfSubsampledImageNotPadded[1],
            zLowToPutTheNotPaddedInSubsampledImPart : zLowToPutTheNotPaddedInSubsampledImPart+dimensionsOfTheSliceOfSubsampledImageNotPadded[2]] = sliceOfSubsampledImageNotPadded
            
    #placeholderReturn = np.ones([3,19,19,19], dtype="float32") #channel, dims 
    return subsampledChannelsForThisImagePart



def shuffleSegmentsOfThisSubepoch(  channelsOfSegmentsForSubepochListPerPathway,
                                    lblsForPredictedPartOfSegmentsForSubepochList ) :
    numOfPathwayWithInput = len(channelsOfSegmentsForSubepochListPerPathway)
    inputToZip = [ sublistForPathway for sublistForPathway in channelsOfSegmentsForSubepochListPerPathway ]
    inputToZip += [ lblsForPredictedPartOfSegmentsForSubepochList ]
    
    combined = list(zip(*inputToZip)) #list() for python3 compatibility, as range cannot get assignment in shuffle()
    random.shuffle(combined)
    shuffledInputListsToZip = list(zip(*combined))
    
    shuffledChannelsOfSegmentsForSubepochListPerPathway = [ sublistForPathway for sublistForPathway in shuffledInputListsToZip[:numOfPathwayWithInput] ]
    shuffledLblsForPredictedPartOfSegmentsForSubepochList = shuffledInputListsToZip[numOfPathwayWithInput]
    
    return [shuffledChannelsOfSegmentsForSubepochListPerPathway, shuffledLblsForPredictedPartOfSegmentsForSubepochList]


# I must merge this with function: extractSegmentsGivenSliceCoords() that is used for Testing! Should be easy!
# This is used in training/val only.
def extractSegmentGivenSliceCoords(train_or_val,
                                   cnn3d,
                                   coordsOfCentralVoxelOfThisImPart,
                                   allChannelsOfPatientInNpArray,
                                   gtLabelsImage) :
    # allChannelsOfPatientInNpArray: numpy array [ n_channels, x, y, z ]
    
    channelsForSegmentPerPathway = []
    # Sampling
    for pathway in cnn3d.pathways[:1] : #Hack. The rest of this loop can work for the whole .pathways...
        # ... BUT the loop does not check what happens if boundaries are out of limits, to fill with zeros. This is done in getImagePartFromSubsampledImageForTraining().
        #... Update it in a nice way to be done here, and then take getImagePartFromSubsampledImageForTraining() out and make loop go for every pathway.
        
        if pathway.pType() == pt.FC :
            continue
        subSamplingFactor = pathway.subsFactor()
        pathwayInputShapeRcz = pathway.getShapeOfInput(train_or_val)[2:]
        leftBoundaryRcz = [ coordsOfCentralVoxelOfThisImPart[0] - subSamplingFactor[0]*(pathwayInputShapeRcz[0]-1)//2,
                            coordsOfCentralVoxelOfThisImPart[1] - subSamplingFactor[1]*(pathwayInputShapeRcz[1]-1)//2,
                            coordsOfCentralVoxelOfThisImPart[2] - subSamplingFactor[2]*(pathwayInputShapeRcz[2]-1)//2]
        rightBoundaryRcz = [leftBoundaryRcz[0] + subSamplingFactor[0]*pathwayInputShapeRcz[0],
                            leftBoundaryRcz[1] + subSamplingFactor[1]*pathwayInputShapeRcz[1],
                            leftBoundaryRcz[2] + subSamplingFactor[2]*pathwayInputShapeRcz[2]]
        
        channelsForThisImagePart = allChannelsOfPatientInNpArray[:,
                                                                leftBoundaryRcz[0] : rightBoundaryRcz[0] : subSamplingFactor[0],
                                                                leftBoundaryRcz[1] : rightBoundaryRcz[1] : subSamplingFactor[1],
                                                                leftBoundaryRcz[2] : rightBoundaryRcz[2] : subSamplingFactor[2]]
        
        channelsForSegmentPerPathway.append(channelsForThisImagePart)
        
    # Extract the samples for secondary pathways. This whole for can go away, if I update above code to check to slices out of limits.
    for pathway_i in range(len(cnn3d.pathways)) : # Except Normal 1st, cause that was done already.
        if cnn3d.pathways[pathway_i].pType() == pt.FC or cnn3d.pathways[pathway_i].pType() == pt.NORM:
            continue
        #this datastructure is similar to channelsForThisImagePart, but contains voxels from the subsampled image.
        dimsOfPrimarySegment = cnn3d.pathways[pathway_i].getShapeOfInput(train_or_val)[2:]
        slicesCoordsOfSegmForPrimaryPathway = [ [leftBoundaryRcz[0], rightBoundaryRcz[0]-1], [leftBoundaryRcz[1], rightBoundaryRcz[1]-1], [leftBoundaryRcz[2], rightBoundaryRcz[2]-1] ] # rightmost  are placeholders here.
        channsForThisSubsampledPartAndPathway = getImagePartFromSubsampledImageForTraining(dimsOfPrimarySegment=dimsOfPrimarySegment,
                                                                                        recFieldCnn=cnn3d.recFieldCnn,
                                                                                        subsampledImageChannels=allChannelsOfPatientInNpArray,
                                                                                        image_part_slices_coords=slicesCoordsOfSegmForPrimaryPathway,
                                                                                        subSamplingFactor=cnn3d.pathways[pathway_i].subsFactor(),
                                                                                        subsampledImagePartDimensions=cnn3d.pathways[pathway_i].getShapeOfInput(train_or_val)[2:]
                                                                                        )
        
        channelsForSegmentPerPathway.append(channsForThisSubsampledPartAndPathway)
        
    # Get ground truth labels for training.
    numOfCentralVoxelsClassifRcz = cnn3d.finalTargetLayer_outputShape[train_or_val][2:]
    leftBoundaryRcz = [ coordsOfCentralVoxelOfThisImPart[0] - (numOfCentralVoxelsClassifRcz[0]-1)//2,
                        coordsOfCentralVoxelOfThisImPart[1] - (numOfCentralVoxelsClassifRcz[1]-1)//2,
                        coordsOfCentralVoxelOfThisImPart[2] - (numOfCentralVoxelsClassifRcz[2]-1)//2]
    rightBoundaryRcz = [leftBoundaryRcz[0] + numOfCentralVoxelsClassifRcz[0],
                        leftBoundaryRcz[1] + numOfCentralVoxelsClassifRcz[1],
                        leftBoundaryRcz[2] + numOfCentralVoxelsClassifRcz[2]]
    lblsOfPredictedPartOfSegment = gtLabelsImage[ leftBoundaryRcz[0] : rightBoundaryRcz[0],
                                                  leftBoundaryRcz[1] : rightBoundaryRcz[1],
                                                  leftBoundaryRcz[2] : rightBoundaryRcz[2] ]
    
    # Make COPIES of the segments, instead of having a VIEW (slice) of them. This is so that the the whole volume are afterwards released from RAM.
    channelsForSegmentPerPathway = [ np.array(pathw_channs, copy=True, dtype='float32') for pathw_channs in channelsForSegmentPerPathway  ]
    lblsOfPredictedPartOfSegment = np.copy(lblsOfPredictedPartOfSegment)
    
    return [ channelsForSegmentPerPathway, lblsOfPredictedPartOfSegment ]




#################################################################################################################################
#                                                                                                                               #
#       Below are functions for testing only. There is duplication with training. They are not the same, but could be merged.   #
#                                                                                                                               #
#################################################################################################################################

# This is very similar to sample_coords_of_segments() I believe, which is used for training. Consider way to merge them.
def getCoordsOfAllSegmentsOfAnImage(log,
                                    dimsOfPrimarySegment, # RCZ dims of input to primary pathway (NORMAL). Which should be the first one in .pathways.
                                    strideOfSegmentsPerDimInVoxels,
                                    batch_size,
                                    channelsOfImageNpArray,
                                    roiMask
                                    ) :
    # channelsOfImageNpArray: np array [n_channels, x, y, z]
    log.print3("Starting to (tile) extract Segments from the images of the subject for Segmentation...")
    
    sliceCoordsOfSegmentsToReturn = []
    
    niiDimensions = list(channelsOfImageNpArray[0].shape) # Dims of the volumes
    
    zLowBoundaryNext=0; zAxisCentralPartPredicted = False;
    while not zAxisCentralPartPredicted :
        zFarBoundary = min(zLowBoundaryNext+dimsOfPrimarySegment[2], niiDimensions[2]) #Excluding.
        zLowBoundary = zFarBoundary - dimsOfPrimarySegment[2]
        zLowBoundaryNext = zLowBoundaryNext + strideOfSegmentsPerDimInVoxels[2]
        zAxisCentralPartPredicted = False if zFarBoundary < niiDimensions[2] else True #THIS IS THE IMPORTANT CRITERION.
        
        cLowBoundaryNext=0; cAxisCentralPartPredicted = False;
        while not cAxisCentralPartPredicted :
            cFarBoundary = min(cLowBoundaryNext+dimsOfPrimarySegment[1], niiDimensions[1]) #Excluding.
            cLowBoundary = cFarBoundary - dimsOfPrimarySegment[1]
            cLowBoundaryNext = cLowBoundaryNext + strideOfSegmentsPerDimInVoxels[1]
            cAxisCentralPartPredicted = False if cFarBoundary < niiDimensions[1] else True
            
            rLowBoundaryNext=0; rAxisCentralPartPredicted = False;
            while not rAxisCentralPartPredicted :
                rFarBoundary = min(rLowBoundaryNext+dimsOfPrimarySegment[0], niiDimensions[0]) #Excluding.
                rLowBoundary = rFarBoundary - dimsOfPrimarySegment[0]
                rLowBoundaryNext = rLowBoundaryNext + strideOfSegmentsPerDimInVoxels[0]
                rAxisCentralPartPredicted = False if rFarBoundary < niiDimensions[0] else True
                
                if isinstance(roiMask, (np.ndarray)) : #In case I pass a brain-mask, I ll use it to only predict inside it. Otherwise, whole image.
                    if not np.any(roiMask[rLowBoundary:rFarBoundary,
                                            cLowBoundary:cFarBoundary,
                                            zLowBoundary:zFarBoundary
                                            ]) : #all of it is out of the brain so skip it.
                        continue
                    
                sliceCoordsOfSegmentsToReturn.append([ [rLowBoundary, rFarBoundary-1], [cLowBoundary, cFarBoundary-1], [zLowBoundary, zFarBoundary-1] ])
                
    #I need to have a total number of image-parts that can be exactly-divided by the 'batch_size'. For this reason, I add in the far end of the list multiple copies of the last element.
    total_number_of_image_parts = len(sliceCoordsOfSegmentsToReturn)
    number_of_imageParts_missing_for_exact_division =  batch_size - total_number_of_image_parts%batch_size if total_number_of_image_parts%batch_size != 0 else 0
    for extra_useless_image_part_i in range(number_of_imageParts_missing_for_exact_division) :
        sliceCoordsOfSegmentsToReturn.append(sliceCoordsOfSegmentsToReturn[-1])
        
    #I think that since the parts are acquired in a certain order and are sorted this way in the list, it is easy
    #to know which part of the image they came from, as it depends only on the stride-size and the imagePart size.
    
    log.print3("Finished (tiling) extracting Segments from the images of the subject for Segmentation.")
    
    # sliceCoordsOfSegmentsToReturn: list with 3 dimensions. numberOfSegments x 3(rcz) x 2 (lower and upper limit of the segment, INCLUSIVE both sides)
    return [sliceCoordsOfSegmentsToReturn]



# I must merge this with function: extractSegmentGivenSliceCoords() that is used for Training/Validation! Should be easy!
# This is used in testing only.
def extractSegmentsGivenSliceCoords(cnn3d,
                                    sliceCoordsOfSegmentsToExtract,
                                    channelsOfImageNpArray,
                                    recFieldCnn) :
    # channelsOfImageNpArray: numpy array [ n_channels, x, y, z ]
    numberOfSegmentsToExtract = len(sliceCoordsOfSegmentsToExtract)
    channsForSegmentsPerPathToReturn = [ [] for i in range(cnn3d.getNumPathwaysThatRequireInput()) ] # [pathway, image parts, channels, r, c, z]
    dimsOfPrimarySegment = cnn3d.pathways[0].getShapeOfInput("test")[2:] # RCZ dims of input to primary pathway (NORMAL). Which should be the first one in .pathways.
    
    for segment_i in range(numberOfSegmentsToExtract) :
        rLowBoundary = sliceCoordsOfSegmentsToExtract[segment_i][0][0]; rFarBoundary = sliceCoordsOfSegmentsToExtract[segment_i][0][1]
        cLowBoundary = sliceCoordsOfSegmentsToExtract[segment_i][1][0]; cFarBoundary = sliceCoordsOfSegmentsToExtract[segment_i][1][1]
        zLowBoundary = sliceCoordsOfSegmentsToExtract[segment_i][2][0]; zFarBoundary = sliceCoordsOfSegmentsToExtract[segment_i][2][1]
        # segment for primary pathway
        channsForPrimaryPathForThisSegm = channelsOfImageNpArray[:,
                                                                rLowBoundary:rFarBoundary+1,
                                                                cLowBoundary:cFarBoundary+1,
                                                                zLowBoundary:zFarBoundary+1
                                                                ]
        channsForSegmentsPerPathToReturn[0].append(channsForPrimaryPathForThisSegm)
        
        #Subsampled pathways
        for pathway_i in range(len(cnn3d.pathways)) : # Except Normal 1st, cause that was done already.
            if cnn3d.pathways[pathway_i].pType() == pt.FC or cnn3d.pathways[pathway_i].pType() == pt.NORM:
                continue
            slicesCoordsOfSegmForPrimaryPathway = [ [rLowBoundary, rFarBoundary-1], [cLowBoundary, cFarBoundary-1], [zLowBoundary, zFarBoundary-1] ] #the right hand values are placeholders in this case.
            channsForThisSubsPathForThisSegm = getImagePartFromSubsampledImageForTraining(  dimsOfPrimarySegment=dimsOfPrimarySegment,
                                                                                            recFieldCnn=recFieldCnn,
                                                                                            subsampledImageChannels=channelsOfImageNpArray,
                                                                                            image_part_slices_coords=slicesCoordsOfSegmForPrimaryPathway,
                                                                                            subSamplingFactor=cnn3d.pathways[pathway_i].subsFactor(),
                                                                                            subsampledImagePartDimensions=cnn3d.pathways[pathway_i].getShapeOfInput("test")[2:]
                                                                                            )
            channsForSegmentsPerPathToReturn[pathway_i].append(channsForThisSubsPathForThisSegm)
            
    return [channsForSegmentsPerPathToReturn]



###########################################
# Checks whether the data is as expected  #
###########################################

def check_gt_vs_num_classes(log, img_gt, num_classes):
    id_str = "["+str(os.getpid())+"]"
    max_in_gt = np.max(img_gt)
    if np.max(img_gt) > num_classes-1 : # num_classes includes background=0
        msg =  id_str+" ERROR:\t GT labels included a label value ["+str(max_in_gt)+"] greater than what CNN expects."+\
                "\n\t In model-config the number of classes was specified as ["+str(num_classes)+"]."+\
                "\n\t Check your data or change the number of classes in model-config."+\
                "\n\t Note: number of classes in model config should include the background as a class."
        log.print3(msg)
        raise ValueError(msg)




