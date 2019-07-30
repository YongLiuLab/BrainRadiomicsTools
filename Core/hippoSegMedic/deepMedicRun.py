#!/usr/bin/env python
# Copyright (c) 2016, Konstantinos Kamnitsas
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the BSD license. See the accompanying LICENSE file
# or read the terms at https://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, print_function, division
import sys
import os
import traceback

sys.setrecursionlimit(20000)

from deepmedic.frontEnd.configParsing.modelConfig import ModelConfig
from deepmedic.frontEnd.configParsing.testConfig import TestConfig
from deepmedic.frontEnd.testSession import TestSession
from deepmedic.frontEnd.configParsing.modelParams import ModelParameters
path = os.path.split(os.path.realpath(__file__))[0]

def str_is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def set_environment(dev_string):
    # Setup cpu / gpu devices.
    sess_device = None
    if dev_string == 'cpu':
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        sess_device = "/CPU:0"
    return (sess_device)

#################################################
#                        MAIN                   #
#################################################
if __name__ == '__main__':
    cwd = os.getcwd()

    abs_path_model_cfg  = os.path.join(path,"./config/modelConfig.cfg")
    model_cfg = ModelConfig( abs_path_model_cfg )
        
    # Create session.
    # if args.train_cfg:
    #     abs_path_train_cfg = getAbsPathEvenIfRelativeIsGiven(args.train_cfg, cwd)
    #     session = TrainSession( TrainConfig(abs_path_train_cfg) )
    # elif args.test_cfg:
    #     abs_path_test_cfg = getAbsPathEvenIfRelativeIsGiven(args.test_cfg, cwd)
    abs_path_test_cfg = os.path.join(path,"./config/testConfig.cfg")
    session = TestSession( TestConfig(abs_path_test_cfg) )
        
    #Create output folders and logger.
    session.make_output_folders()
    session.setup_logger()
    
    log = session.get_logger()
    
    log.print3("")
    log.print3("======================== Starting new session ============================")
    
    #check_dev_passed_correctly("cpu")
    (sess_device) = set_environment("cpu")
    #log.print3("Available devices to Tensorflow:\n" + str(device_lib.list_local_devices()))
    
    try:
        #Find out what session we are being asked to perform:
         # Should be always true.
        log.print3("CONFIG: The configuration file for the [model] given is: " + str( model_cfg.get_abs_path_to_cfg() ))
        model_params = ModelParameters( log, model_cfg )
        model_params.print_params()
            
        # Sessions
        log.print3("CONFIG: The configuration file for the [session] was loaded from: " + str(session.get_abs_path_to_cfg() ))
        #session.override_file_cfg_with_cmd_line_cfg(args)
        _ = session.compile_session_params_from_cfg(model_params)

        session.run_session(sess_device, model_params)
        # All done.
    except (Exception, KeyboardInterrupt) as e:
        log.print3("")
        log.print3("ERROR: Caught exception from main process: " + str(e) )
        log.print3( traceback.format_exc() )
        
    log.print3("Finished.")
    
        
