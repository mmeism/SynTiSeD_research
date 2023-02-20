import copy
import random
import sys
import numpy as np
import pandas as pd


class ResidentDictionary(dict):
    """
    Initialize a ResidentDictionary from dict
    """
    def add_resident(self, name: str, action_sequences_list, variance: int = None):
        """
        Add an resident with the given parameters to the ResidentDictionary

        Parameters
        ----------
        name : str
            name of the resident

        action_sequences_list : ActionSequenceList
            list of ActionSequences according to which the resident can act

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamps of the action.

        """
        if name in self:
            print(f'Error: Resident was not initialized correctly. '
                  f'Resident "{name}" already exists in dictionary. '
                  f'Please choose another name.')
            sys.exit()
        else:
            self[name] = _Resident(name, action_sequences_list, variance)


class _Resident:
    def __init__(self, name: str, action_sequences_list, variance: int = None):
        """
        Initialize a resident with the given parameters

        Parameters
        ----------
        name : str
            name of the resident

        action_sequences_list : ActionSequenceList
            list of ActionSequences according to which the resident can act

        variance : int
            optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero,
            in which a value is randomly selected, that is added or subtracted to the timestamps of the action.
        """
        self.name = name
        self.action_sequences_list = action_sequences_list
        self.variance = variance

        self.current_action_sequence = []
        self.action_seq_iterator = 0

        self.next_appliances_to_activate = []

    def step(self, timestamp: int):
        """
        Check if the resident has to activate an Appliance and if yes do so

        Parameters
        ----------
        timestamp : int
            current timestamp of the day

        """
        if self.next_appliances_to_activate:
            if not self.next_appliances_to_activate[0].is_appliance_in_use(timestamp):
                appliance = self.next_appliances_to_activate[0]
                power_consumption_pattern = appliance.pick_new_power_consumption_pattern()
                power_consumption_pattern.index += timestamp
                power_consumption_pattern = power_consumption_pattern.reindex(list(range(0, power_consumption_pattern.index.max()+1)), fill_value=0)
                self.current_action_sequence[(self.action_seq_iterator-1)].end_timestamp = int(power_consumption_pattern.iloc[::-1].ne(0).idxmax().iloc[0])
                if appliance.power_consumption_pattern.empty:
                    appliance.power_consumption_pattern = pd.DataFrame([np.nan] * timestamp)
                appliance.power_consumption_pattern = pd.concat(
                    [appliance.power_consumption_pattern, power_consumption_pattern], axis=1)
                appliance.power_consumption_pattern = pd.DataFrame(appliance.power_consumption_pattern.sum(axis=1))
                appliance.power_consumption_pattern = appliance.power_consumption_pattern.rename(
                    columns={appliance.power_consumption_pattern.columns[0]: appliance.name})
                self.next_appliances_to_activate.pop(0)

    def pick_action_sequence_consecutively(self, iterator: int):
        """
        Pick a ActionSequence from the assigned list of ActionSequences
        as the current ActionSequence

        Parameters
        ----------
        iterator : int
            iterator to consecutively iterate over the assigned ActionSequences

        """
        self.next_appliances_to_activate = []
        self.action_seq_iterator = 0
        number = iterator % len(self.action_sequences_list)
        self.current_action_sequence = copy.deepcopy(self.action_sequences_list[number])
        self.current_action_sequence = self.vary_timestamps_in_action_seq(self.current_action_sequence)

    def vary_timestamps_in_action_seq(self, action_seq: list):
        """
        Vary the timestamps of the Actions of an action sequence with a certain variance

        Parameters
        ----------
        action_seq : list
            list with a sequence of Actions

        Returns
        -------
        action_seq : list
            returns a list with a sequence of Actions with varied timestamps
        """
        top_level_variance = None
        if self.current_action_sequence.variance is not None:
            top_level_variance = self.current_action_sequence.variance
        if self.variance is not None:
            top_level_variance = self.variance

        for action in list(action_seq):
            if action.probability >= random.uniform(0, 1):
                if top_level_variance is None:
                    variance = action.variance
                else:
                    variance = top_level_variance
                action.start_timestamp = action.start_timestamp + random.randint(-variance, variance)
            else:
                action_seq.remove(action)
        ## sort actions by their timestamps in case
        action_seq.sort(key=lambda x: x.start_timestamp)
        return action_seq
