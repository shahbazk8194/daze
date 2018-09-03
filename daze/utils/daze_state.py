'''
The loading and saving of daze state
'''
import os
import pickle

from ..errors import DazeStateException


DAZE_STORAGE = '~/.daze_data.pkl'


def save_state(new_data):
    '''
    Save daze data into appropriate location
    '''
    try:
        daze_data = load_state()
    except DazeStateException:
        daze_data = new_data
    else:
        daze_data.update(new_data)

    with open(os.path.expanduser(DAZE_STORAGE), 'wb') as handle:
        pickle.dump(daze_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_state():
    try:
        with open(os.path.expanduser(DAZE_STORAGE), 'rb') as handle:
            daze_data = pickle.load(handle)
    except OSError as e:
        raise DazeStateException('No daze data to load!')
    else:
        return daze_data

