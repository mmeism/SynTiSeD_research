import os
from datetime import datetime


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def create_directory(directory_path):
    """
    Creates a directory with a given path, if it is not existing.

    Parameters
    ----------
    directory_path : str
        resource path to the directory
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError:
        print('Error: Creating directory. ' + directory_path)


def save_action_sequence(action_seq, filepath, timestamp, avatar_name=''):
    """
    Save an action sequence given a day (00:00:00 timestamp of a day) to a folder.

    Parameters
    ----------
    action_seq : list
        list with a sequence of actions

    filepath : str
        path to the folder where the data is stored

    timestamp : int
        00:00:00 timestamp of the stored day

    avatar_name : str
        name of the resident; optional, if set resident name part of file name

    Returns
    -------
    out : list
        returns a list with the stored sequence of actions
    """
    act_seq_list = []
    date_obj = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    if avatar_name == '':
        path = filepath + '/ActionSeq_' + date_obj + '.txt'
    else:
        path = filepath + '/ActionSeq_' + date_obj + '_' + avatar_name + '.txt'
    with open(path, 'w') as f:
        for action in action_seq:
            time = datetime.fromtimestamp(action.timestamp + timestamp).strftime("%H:%M:%S")
            f.write('"' + str(action.name) + '", ' + str(time) + ', ' + str(action.probability) + '\n')
            act_seq_list.append([str(action.name), str(time), str(action.probability)])
    return act_seq_list

