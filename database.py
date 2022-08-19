import numpy as np
from collections import defaultdict
import pickle


# initializing default dictionary with default value = None
# and songID dictionary with default value also = None

fingerprints = defaultdict(None)
songID = defaultdict(None)

def addFingerprint(prints: list):  #fp (1,2,3) : [(1,2), (1,3)] --song
    
    # fingerprints.py returns a list of fingerprints and a list of times
    # so we probably have to change our parameters - Josh
    # check out fingerprints in fingerprints.py 
    
    # we can steal Ryan's code for this function too -
    # for (fm, fn, dt), tm in key:
    #    database[(fm, fn, dt)].append(("song-j", tm))

    """
    Adds fingerprint key/value pair to the fingerprints dictionary

    Parameters
    ----------
    key: tuple, shape = [(float, float, float), int, float]
        list of fingerprints with each element in the form [(f_i, f_j, ∆t_ij), ti, id]
    """
    for key, id, time in prints:
        if key not in fingerprints:
            fingerprints[key] = [(id, time)]
        else:
            fingerprints[key].append((id, time))
 
def removeFingerprint(key: tuple, value: tuple):
    """
    Removes input fingerprint from dictionary 
    
    Parameters
    ----------
    key: tuple, shape = [int, int, int]
        fingerprint in the form (f_i, f_j, ∆t_ij)
    
    value: tuple, shape = [int, int]
        Tuple containing songID and time pair.
    """

    if key not in fingerprints:
        return "No such finger print exists :("
    else:
        values = fingerprints[key]
        if len(values) == 1:
            del(fingerprints[key])
        else:
            values.remove(value)
            fingerprints[key] = values

def saveFingerprints():
    """
    Saves the fingerprints dictionary as fingerprints.pkl
    """
    with open("fingerprints.pkl", mode="wb") as opened_file:
        pickle.dump(fingerprints, opened_file)

def loadFingerprints():
    """
    Loads fingerprints.pkl and returns it as a dictionary
    
    Returns
    --------
    defaultdict
        defaultdict containing the saved fingerprints
    """
    with open("fingerprints.pkl", mode="rb") as opened_file:
        fingerprints1 = pickle.load(opened_file)
    return fingerprints1

def getFingerprint(key: tuple):
    """
    Gets all times in all songs where a certain fingerprint occurs
    
    Parameters
    -----------
    key : tuple, shape = (3, )
        The fingerprint whos times and songs we want to retrieve

    Returns
    ------------
    List[Tuple[int, int]]
        List of tuples containing songIDs and times
    """
    try: 
        return fingerprints[key]
    except:
        return []


def addSongID(id: int, songInfo: tuple): 
    """
    Add new song ID and informatino to the songID dictionary

    Parameters
    ----------
    id: int
        Value of the song ID to be added
    
    songInfo: tuple[string, string]
        Tuple containing the song name and artist
    """
    songID[id] = [songInfo]
    
def removeSongID(id: int):
    """
    Removes input id from songID dictionary 

    Parameters
    -----------
    id: int
        Value of the song ID to be removed
    """
    if id in songID:
        del songID[id]     

def saveSongIDs():
    """
    Saves the songID dictionary as songID.pkl
    """
    with open("songID.pkl", mode="wb") as opened_file:
        pickle.dump(songID, opened_file)
        
def loadSongIDs():
    """
    Loads songID.pkl and returns it as defaultdict

    Returns
    --------
    defaultdict
        Contains the saved song IDs and song info.
    """
    with open("songID.pkl", mode="rb") as opened_file:
        songID1 = pickle.load(opened_file)
    return songID1

def getSong (key: int):
    """
    Gets name of song from songID dictionary given its songID.

    return
    -------
        tuple[string, string]
            Contains the song name and artist
    """
    try: 
        return songID[key]
    except:
        return []

def generateID(songN: str):

    """
    Generates a new ID and SongName pairing and adds it into the SongID dict

    Parameters
    -----------
    songN: String
        Name of the song

    return
    -------
        NewId: int
            ID of the song added to songID dict

    """

    try:
        newID = max(songID) + 1
    except:
        newID = 1

    return newID

'''
addFingerprint([[(1, 2, 3), 4, 1], [(1, 2, 3), 5, 1], [(1, 2, 3), 6, 2]])
addFingerprint([[(4, 5, 6), 4, 3]])
print(fingerprints)
removeFingerprint((4, 5, 6), (4, 1))
'''

'''
addSongID(1, ("Halo Theme", "Ryan Soklaski"))
addSongID(2, ('Waluigiverse', 'Ryan Soklaski'))
addSongID(3, ('Never Gonna Give You Up', 'Ryan Soklaski'))
addSongID(4, ("Song of Storms", 'Ryan Soklaski'))
addSongID(2, ("Cotton Eye Joe", 'Ryan Soklaski'))
removeSongID(3)
removeSongID(2)
removeSongID(3)
print(songID)
saveSongIDs()
'''
