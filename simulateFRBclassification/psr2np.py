# /usr/local/python2

import psrchive as psr
import numpy as np
from tqdm import tqdm
import argparse
import glob

def psr2np(fname, NCHAN, dm):
    # Get psrchive file as input and outputs numpy array
    fpsr = psr.Archive_load(fname)

    # must disperse the signal then dedisperse due to crashes on already dedispersed signals
    fpsr.dededisperse()
    fpsr.set_dispersion_measure(dm)
    fpsr.dedisperse()

    # resize image to number of frequency channels
    fpsr.fscrunch_to_nchan(NCHAN)
    fpsr.remove_baseline()

    # -- apply weights for RFI lines --#
    ds = fpsr.get_data().squeeze()
    w = fpsr.get_weights().flatten()
    w = w / np.max(w)
    idx = np.where(w == 0)[0]
    ds = np.multiply(ds, w[np.newaxis, :, np.newaxis])
    ds[:, idx, :] = np.nan

    # -- Get total intensity data (I) from the full stokes --#
    data = ds[0, :, :]

    # -- Get frequency axis values --#
    freq = np.linspace(fpsr.get_centre_frequency() - abs(fpsr.get_bandwidth() / 2),
                       fpsr.get_centre_frequency() + abs(fpsr.get_bandwidth() / 2), fpsr.get_nchan())

    # -- Get time axis and convert to milliseconds --#
    tbin = float(fpsr.integration_length() / fpsr.get_nbin())
    taxis = np.arange(0, fpsr.integration_length(), tbin) * 1000
    
    return data
    # test this after verifying returning only the data
    # return np.array([data, freq, taxis])

if __name__ == "__main__":
    # Read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='/home/vgajjar/example_archive/')
    parser.add_argument('--save_name', type=str, default='psr_arrays.npy',
                        help='Filename to save frequency-time arrays')
    parser.add_argument('--NCHAN', type=int, default=64,
                        help='Number of frequency channels to resize psrchive files to')
    parser.add_argument('--NTIME', type=int, default=256, help='Number of time bins')
    
    args = parser.parse_args()

    path = args.path
    save_name = args.save_name
    NCHAN = args.NCHAN
    NTIME = args.NTIME
    DM = 102.4

    if path is not None:
        files = glob.glob(path + "*.ar")
    else:    
        files = glob.glob("*.ar")
   
    psrchive_data = [] 
    # label = []

    for filename in tqdm(files):
        # transform ar file into numpy array and append to list
        psrchive_data.append(psr2np(filename, NCHAN, DM))
        # label.append(0)
        # ar file with injected FRB
        # label.append(1)

    # save final array to disk
    np.save(save_name, np.array(psrchive_data))
