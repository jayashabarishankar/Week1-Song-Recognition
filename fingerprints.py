import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import database as db
from microphone import record_audio
import defaults

from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure
from scipy.ndimage.morphology import iterate_structure
from numba import njit
from typing import Tuple, Callable, List



def samples_to_spectrogram(samples, sampling_rate):

    #
    """
    Turns audio samples into spectrogram
    Parameters
    ----------
    sampling_rate : int, 
        the sampling rate (44100 Hz)
    audio_samples : np.array
        audio samples from mp3 or microphone
        
    Returns
    --------
        spectogram of audio samples

    """
    spectrogram, freqs, times = mlab.specgram(
        samples,
        NFFT=4096,
        Fs=sampling_rate,
        window=mlab.window_hanning,
        noverlap=int(4096 // 2)
    )

    spectrogram = np.clip(spectrogram, 10**-20, None)
    spectrogram = np.log(spectrogram)
    
    # finding min amplitude

    percentile = defaults.MIN_FRAC_AMP_CUTOFF

    log_S = spectrogram.ravel()  # ravel flattens 2D spectrogram into a 1D array
    ind = round(len(log_S) * percentile)  # find the index associated with the 75th percentile log-amplitude
    cutoff_log_amplitude = np.partition(log_S, ind)[ind]  # find the actual 75th percentile log-amplitude
    

    return spectrogram, cutoff_log_amplitude

#peaks function 
base_structure = generate_binary_structure(2,1)
neighborhood = iterate_structure(base_structure, 20)

@njit
def _peaks(
    data_2d: np.ndarray, nbrhd_row_offsets: np.ndarray, nbrhd_col_offsets: np.ndarray, amp_min: float
) -> List[Tuple[int, int]]:
    
    """
    Finds and returns peaks in a spectrogram
    Parameters
    ----------
    data_2d : numpy.ndarray, shape-(H, W)
        The 2D array of data in which local peaks will be detected.

    nbrhd_row_offsets : numpy.ndarray, shape-(N,)
        The row-index offsets used to traverse the local neighborhood.
        
        E.g., given the row/col-offsets (dr, dc), the element at 
        index (r+dr, c+dc) will reside in the neighborhood centered at (r, c).
    
    nbrhd_col_offsets : numpy.ndarray, shape-(N,)
        The col-index offsets used to traverse the local neighborhood. See
        `nbrhd_row_offsets` for more details.
        
    amp_min : float
        All amplitudes equal to or below this value are excluded from being
        local peaks.
    
    Returns
    -------
    List[Tuple[int, int]]
        (row, col) index pair for each local peak location, returned in 
        column-major order
    """

    peaks = []  # stores the (row, col) locations of all the local peaks

    for c, r in np.ndindex(*data_2d.shape[::-1]):
        if data_2d[r, c] <= amp_min:
            # The amplitude falls beneath the minimum threshold
            # thus this can't be a peak.
            continue
        
        # Iterating over the neighborhood centered on (r, c) to see
        # if (r, c) is associated with the largest value in that
        # neighborhood.

        # dr: offset from r to visit neighbor
        # dc: offset from c to visit neighbor
        for dr, dc in zip(nbrhd_row_offsets, nbrhd_col_offsets):
            if dr == 0 and dc == 0:
                # This would compare (r, c) with itself.. skip!
                continue
            if not (0 <= r + dr < data_2d.shape[0]):
                # neighbor falls outside of boundary.. skip!
                continue
            if not (0 <= c + dc < data_2d.shape[1]):
                # neighbor falls outside of boundary.. skip!
                continue
            if data_2d[r, c] < data_2d[r + dr, c + dc]:
                # One of the amplitudes within the neighborhood
                # is larger, thus data_2d[r, c] cannot be a peak
                break
        else:
            # if we did not break from the for-loop then (r, c) is a local peak
            peaks.append((r, c))
    return peaks
    
#this calculates the cutoff for the amplitudes of the peaks


def find_min_amp(spectrogram, percentile=defaults.MIN_FRAC_AMP_CUTOFF):
    """
    Identified as 75th percentile amplitude from spectrogram.
    Finds minimum threshold for amplitude such that peaks are significant. 
    """
    log_S = np.log(spectrogram).ravel()  # ravel flattens 2D spectrogram into a 1D array
    ind = round(len(log_S) * percentile)  # find the index associated with the 75th percentile log-amplitude
    cutoff_log_amplitude = np.partition(log_S, ind)[ind]  # find the actual 675th percentile log-amplitude
    return cutoff_log_amplitude


def local_peak_locations(data_2d: np.ndarray, neighborhood: np.ndarray, amp_min: float):
    """
    Parameters
    ----------
    data_2d : numpy.ndarray, shape-(H, W)
        The 2D array of data in which local peaks will be detected
    
    neighborhood : numpy.ndarray, shape-(h, w)
        A boolean mask indicating the "neighborhood" in which each
        datum will be assessed to determine whether or not it is
        a local peak. h and w must be odd-valued numbers
        
    amp_min : float
        All amplitudes at and below this value are excluded from being local 
        peaks.
    
    Returns
    -------
    List[Tuple[int, int]]
        (row (time window), col (frequency) ) index pair for each local peak location, returned
        in column-major ordering.
    
    """
    
    assert neighborhood.shape[0] % 2 == 1
    assert neighborhood.shape[1] % 2 == 1

    nbrhd_row_indices, nbrhd_col_indices = np.where(neighborhood)
    

    nbrhd_row_indices = nbrhd_row_indices - neighborhood.shape[0] // 2
    nbrhd_col_indices = nbrhd_col_indices - neighborhood.shape[1] // 2

    return _peaks(data_2d, nbrhd_row_indices, nbrhd_col_indices, amp_min=amp_min)
                


#fingerprints


def fingerprints(peaks: np.ndarray, songID : int, fanout = 15):
    
    """
    Parameters:
        peaks : List[Tuple[int, int]]
            (row, col) index pair for each local peak location in column-major order
        
        fanout: int 
            Numbers of nearest peak connectionns

        songID : int
            Unique song ID     
    
    Returns:
    
        fingerprints : List[Tuple[float, float, float]]
            (initial peak frequency, fanout peak frequency, time between peaks)
    
        times:  List[float]
            time in which the fingerprint occurs in recording
    """
    id = songID
    fingerprints = []
#   time_i = []

    for i in range(len(peaks)):
      
        for j in range(1, min(fanout + 1, len(peaks) - i)):
            
            fi = peaks[i][0]
            fj = peaks[i + j][0]
            ti = peaks[i][1] # flag!
            tj = peaks[i+j][1]
            
            #fingerprints.append([(fi, fj, tj - ti), ti])
            fingerprints.append([(fi, fj, tj - ti), id, ti])

     #works? idk to add fingerprint to database
    
    return fingerprints

            
