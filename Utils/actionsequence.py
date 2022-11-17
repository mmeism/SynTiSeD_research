import glob
from datetime import datetime
from pathlib import Path


class ActionSequenceList(list):
    """
    Initialize an list of ActionSequence from list.
    """

    def append_action_seq(self, name, path, variance=None):
        """
        Append a new ActionSequence with the given parameters to the ActionSequenceList.

        Parameters
        ----------
        name : str
            name of the action sequence

        path : str
            resource path to the action sequence

        variance : int
            optional, default = None; variance parameter in seconds; for each appliance, the variance spans an interval
            with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action
        """
        self.append(_ActionSequence(name, path, variance))

    def append_action_seq_folder(self, path, variance=None):
        """
        Append a new folder of ActionSequences with the given parameters to the ActionSequenceList.

        Parameters
        ----------
        path : str
            resource path to the folder of action sequences

        variance : int
            optional, default = None; variance parameter in seconds; for each appliance, the variance spans an interval
            with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action
        """
        for filepath in glob.iglob(path + '/*.txt'):
            name = Path(filepath).stem
            self.append(_ActionSequence(name, filepath, variance))


class _ActionSequence(list):
    def __init__(self, name, path, variance=None):
        """
        Initialize an ActionSequence with the given parameters from list.

        Parameters
        ----------
        name : str
            name of the action sequence

        path : str
            resource path to the action sequence

        variance : int
            optional, default = None; variance parameter in seconds; for each appliance, the variance spans an interval
            with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action
        """
        self.name = name
        self.path = path
        self.variance = variance

        self.text_data = ''
        self.load_action_sequence_text_data(self.path)
        self.convert_action_sequence_str_to_list(self.text_data)

    def load_action_sequence_text_data(self, filepath):
        """
        Read an action sequence text file from resource path.

        Parameters
        ----------
        filepath : str
            path to resource
        """
        self.text_data = open(filepath, 'r').read()

    def convert_action_sequence_str_to_list(self, act_seq_str):
        """
        Transform an action sequence string to a list.

        Parameters
        ----------
        act_seq_str : str
            action sequence in string format
        """
        act_seq_str_list = act_seq_str.split('\n')
        for action_str in act_seq_str_list:
            action_str_list = action_str.split(',')
            # if a line in txt file has less than 3 properties or more than 4, skip it
            if 3 <= len(action_str_list) <= 4:
                action_str_list[0] = action_str_list[0].strip('"')
                time = datetime.strptime(action_str_list[1].strip(), "%H:%M:%S")
                action_str_list[1] = (time.hour * 3600) + (time.minute * 60) + time.second
                # Check if there is a variance in txt file defined
                if len(action_str_list) < 4:
                    self.append(_Action(action_str_list[0], action_str_list[1], float(action_str_list[2])))
                else:
                    self.append(_Action(action_str_list[0], action_str_list[1], float(action_str_list[2]),
                                        int(action_str_list[3])))
        self.sort(key=lambda x: x.timestamp)


class _Action:
    def __init__(self, name, timestamp, probability, variance=0):
        """
        Initialize an action with the given parameters.

        Parameters
        ----------
        name : str
            name of the action

        timestamp : int
            timestamp of the day in seconds starting from 00:00:00

        probability : float
            value from 0 to 1, representing the probability if an action is happening

        variance : int
            optional, default = 0; variance parameter in seconds; for each appliance, the variance spans an interval
            with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action
        """
        self.name = name
        self.timestamp = timestamp
        self.probability = float(probability)
        self.variance = variance
