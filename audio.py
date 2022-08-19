#!/usr/bin/env python
# coding: utf-8



# In[8]:


import numpy as np
import defaults
from IPython.display import Audio
from microphone import record_audio
from scipy.ndimage.morphology import generate_binary_structure
from scipy.ndimage.morphology import iterate_structure
import librosa
import database as db
import defaults
import matching
import fingerprints as fp
import random 
# In[7]:


def mic_input(listen_time): 
    """
    converts audio recorded with microphone to numpy array
    
    Parameters
    ----------
    listen_time: int
        length of recording
    """
    frames, sampling_rate = record_audio(listen_time)
    samples = np.hstack([np.frombuffer(i, np.int16) for i in frames])
    return samples, sampling_rate
    
def mp3_input(file_path, songName = None, artist = None):
    """
    converts mp3 file to numpy array, while having optional arguments
    for song name and artist(s).
    
    Parameters
    ----------
    file_path: String
        path to saved audio
    """

    if songName == None:
        songName = input("Enter the name of your MP3 file/song: ")

    if artist == None:
        artist = input("Enter the artist(s) of your MP3 file/song: ")
    
    
    samples, sampling_rate = librosa.load(file_path, sr=44100, mono=True)

    spectroG, cutoff = fp.samples_to_spectrogram(samples, sampling_rate)
    base_structure = generate_binary_structure(2,1)
    neighborhood = iterate_structure(base_structure, 20)

    L_peaks = fp.local_peak_locations(spectroG, neighborhood, cutoff)
    id = db.generateID(songName)
    fingers = fp.fingerprints(L_peaks, id)
    
    db.addFingerprint(fingers)


    db.addSongID(id, (songName, artist))

    return samples, sampling_rate, songName


def mic_input_split(listen_time): 
    """
    converts audio recorded with microphone to numpy array and splits it into samples
    
    Parameters
    ----------
    listen_time: int
        length of recording
    """

    splits = int(input("How would you like to split the audio? (int): "))

    frames, sampling_rate = record_audio(listen_time)
    samples = np.hstack([np.frombuffer(i, np.int16) for i in frames])
    
    # splitting sample:
    split_samples = samples.array_split(splits)

    return random.choice(split_samples), sampling_rate
# In[ ]:
