import os
import sys
from Core import setting
from Core import utils
sys.path.append(setting.path)
def  BrainExtractFast(input,output):
    '''
    :param input:
    :param output:
    :return:
    use FSL . bet2  ， faster than HD-BET
    '''

    # is the input is dir? or file?
    import subprocess
    images = []
    outputImages = []
    if os.path.isdir(input):
        if not os.path.exists(output):
            os.mkdir(output)
        images = utils.checkDir(input)
        if(len(images) == 0):
            print("there is no images in the input dir")
            return
        for image in images:
            outputImages.append(os.path.join(output,"Bet_"+os.path.basename(image)))
    else:
        images.append(input)
        outputImages.append(output)
    exPath = os.path.join(setting.path, "bet", "bet2.exe")

    for image,outputImage in zip(images,outputImages):
        task = subprocess.Popen('%s %s %s' % (exPath, image, outputImage), shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        msg = ''
        for line in task.stdout.readlines():
            msg += line.decode("gb2312")
        status = task.wait()
        print(msg)

def  BrainExtract(input_file_or_dir,output_file_or_dir,mode=True):
    '''

    :param input_file_or_dir:
    :param output_file_or_dir:
    :param mode: fast or acc True/False
    :return:
    '''
    from Core.bet.run import run_hd_bet
    from Core.bet.utils import maybe_mkdir_p, subfiles
    if output_file_or_dir is None:
        output_file_or_dir = os.path.join(os.path.dirname(input_file_or_dir),
                                          os.path.basename(input_file_or_dir).split(".")[0] + "_bet")
    assert os.path.abspath(input_file_or_dir) != os.path.abspath(output_file_or_dir), "output must be different from input"
    if os.path.isdir(input_file_or_dir):
        maybe_mkdir_p(output_file_or_dir)
        input_files = subfiles(input_file_or_dir, suffix='.nii.gz', join=False)

        if len(input_files) == 0:
            raise RuntimeError("input is a folder but no nifti files (.nii.gz) were found in here")

        output_files = [os.path.join(output_file_or_dir, i) for i in input_files]
        input_files = [os.path.join(input_file_or_dir, i) for i in input_files]
    else:
        if not output_file_or_dir.endswith('.nii.gz'):
            output_file_or_dir += '.nii.gz'
            assert os.path.abspath(input_file_or_dir) != os.path.abspath(output_file_or_dir), "output must be different from input"

        output_files = [output_file_or_dir]
        input_files = [input_file_or_dir]

    run_hd_bet(input_files, output_files,mode=mode)
