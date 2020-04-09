#!/usr/bin/python
import subprocess as sp
import sys

"""Run predict.py on a bunch of files at once. Takes in a text file
containing the paths to filterbank files to predict on, as well as
the directory dir_predict that houses the FRBcand file and where the
FRBcand_prob.txt file will be saved to."""

if len(sys.argv) != 4:
    raise ValueError("Invalid number of arguments")
else:
    txt_file, model, dir_predict = str(sys.argv)[1:]

# read every file in A00_Cband_files
with open(txt_file) as f:
    fil_files = f.readlines()
    fil_files = [x.strip() for x in fil_files] # remove whitespace characters

# set up commands to predict

for i, fil_file in enumerate(fil_files):
    try:
        mjd = sp.check_output(["header", fil_file, "-tstart"]).strip()
        split = mjd.split('.') # split mjd and get first 4 decimal places

        # combine everything to get directory to predict files
        spandak_dir = dir_predict + 'BLGCsurvey_Cband_A00_' + split[0] + '_' + split[1][:4]
        path_to_FRBcand = spandak_dir + '/FRBcand'

        # predict using model on candidates in fil_file with coordinates in FRBcand file
        # save pngs of predicted FRBs to disk and FRBcand_prob.txt to same folder as
        # wherever the FRBcand file is (probably spandak_dir)
        cmd = "python predict.py" + \
            " {0} {1} {2} ".format(model, fil_file, path_to_FRBcand) + \
            "--save_predicted_FRBs /datax/scratch/dleduc/predicted_FRBs/{}".format('BLGCsurvey_Cband_A00_' + split[0] + '_' + split[1][:4])

        # execute the command
        print('Predicting on file {0} / {1}'.format(i+1, len(fil_files)))
        print(cmd + '\n')
        proc = sp.call(cmd, shell=True)

    except sp.CalledProcessError:
        continue

    except KeyboardInterrupt:
        proc.kill()
