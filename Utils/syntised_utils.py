import os
import pandas as pd
from pathlib import Path
from datetime import datetime

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def create_directory(directory_path: str):
    """
    Creates a directory with a given path, if it is not existing

    Parameters
    ----------
    directory_path : str
        resource path to the directory
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError:
        print(f'Error: Creating directory. {directory_path}')


def save_action_sequence(action_seq: list, filepath: str, timestamp: int, avatar_name: str = ''):
    """
    Save an action sequence given a day (00:00:00 timestamp of a day) to a folder

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

    """
    date_obj = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    if avatar_name == '':
        path = f'{filepath}/ActionSeq/ActionSeq_{date_obj}.csv'
    else:
        path = f'{filepath}/ActionSeq/ActionSeq_{date_obj}_{avatar_name}.csv'
    with open(path, 'w') as f:
        f.write(f'name,start_time,end_time\n')
        for action in action_seq:
            start_time = datetime.utcfromtimestamp(action.start_timestamp + timestamp).strftime("%H:%M:%S")
            if action.end_timestamp == None:
                f.write(f'"{action.name}",{date_obj} {start_time}\n')
            else:
                end_time = datetime.utcfromtimestamp(action.end_timestamp + timestamp).strftime("%H:%M:%S")
                f.write(f'"{action.name}",{date_obj} {start_time},{date_obj} {end_time}\n')
    return path


def save_apl_active_phases(input_filepath: str, output_filepath: str, resampling: int = 1):
    """
    Save the active phases of the appliances given an input file an action sequence input file

    Parameters
    ----------
    input_filepath : str
        path where the input data is loaded

    output_filepath : str
        path where the output data is stored

    resampling : int
        resampling rate of the output

    """
    input_df = pd.read_csv(input_filepath)
    appliances = input_df['name'].str.split(';\s*', expand=True).stack().unique().tolist()
    df = pd.DataFrame(0, index=range(0, 86400, resampling), columns=appliances)
    df.index = pd.to_datetime(df.index, unit='s', origin=pd.Timestamp(input_df.iloc[0, 1].split(" ")[0]))
    df.index.name = 'timestamp'
    for index, row in input_df.iterrows():
        df.loc[pd.to_datetime(row[1]):pd.to_datetime(row[2]), row[0]] = 1

    file_name = Path(input_filepath).stem
    parent_folder = Path(input_filepath).parent.parent
    df.to_csv(f'{parent_folder}/ActionSeq_active_phases/{file_name}_active_phases.csv')

