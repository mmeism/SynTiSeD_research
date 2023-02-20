import glob
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np


class ActionSequenceList(list):
    """
    Initialize an list of ActionSequence from list
    """

    def append_action_seq(self, name: str, path: str, variance: int = None):
        """
        Append a new ActionSequence with the given parameters to the ActionSequenceList

        Parameters
        ----------
        name : str
            name of the action sequence

        path : str
            resource path to the action sequence

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamp of the action.
        """
        self.append(_ActionSequence(name, path, variance))

    def append_action_seq_folder(self, path: str, variance: int = None):
        """
        Append a new folder of ActionSequences with the given parameters to the ActionSequenceList

        Parameters
        ----------
        path : str
            resource path to the folder of action sequences

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamp of the action.
        """
        for filepath in glob.iglob(f'{path}/*.csv'):
            name = Path(filepath).stem
            self.append(_ActionSequence(name, filepath, variance))


class _ActionSequence(list):
    def __init__(self, name: str, path: str, variance: int = None):
        """
        Initialize an ActionSequence with the given parameters from list

        Parameters
        ----------
        name : str
            name of the action sequence

        path : str
            resource path to the action sequence

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamp of the action.
        """
        self.name = name
        self.path = path
        self.variance = variance

        self.load_action_sequence_data(self.path)

    def load_action_sequence_data(self, filepath: str):
        """
        Read and load an action sequence csv file from resource path

        Parameters
        ----------
        filepath : str
            path to resource
        """
        input_data = pd.read_csv(filepath)
        input_data = input_data.replace(r'^\s*$', np.nan, regex=True)
        for index, row in input_data.iterrows():
            name = row[0].strip('"')
            start_time = datetime.strptime(row[1].strip(), "%H:%M:%S")
            start_time = (start_time.hour * 3600) + (start_time.minute * 60) + start_time.second
            # end_time =
            probability = 1 if pd.isna(row[3]) else row[3]
            variance = 0 if pd.isna(row[4]) else row[4]
            self.append(_Action(name=name, start_timestamp=start_time, probability=float(probability), variance=int(variance)))
        self.sort(key=lambda x: x.start_timestamp)


class _Action:
    def __init__(self,
                 name: str, start_timestamp: int, end_timestamp: int = None, probability: float = 1, variance: int = 0):
        """
        Initialize an action with the given parameters

        Parameters
        ----------
        name : str
            name of the action

        start_timestamp : int
            start timestamp of the day in seconds starting from 00:00:00

        end_timestamp : int
            optional; end timestamp of the day in seconds starting from 00:00:00

        probability : float
            value from 0 to 1, representing the probability if an action is happening

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamp of the action.
        """
        self.name = name
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.probability = float(probability)
        self.variance = variance
