import glob
import pickle
import random
import requests
import copy
import sys
import numpy as np
import pandas as pd


class ApplianceDictionary(dict):
    """
    Initialize a ApplianceDictionary from dict.
    """
    def add_appliance(self, name, path):
        """
        Add an appliance with the given parameters to the ApplianceDictionary.

        Parameters
        ----------
        name : str
            name of the appliance

        path : str
            resource path to power consumption pattern data

        """
        if name in self:
            print('Error: Appliance was not initialized correctly. '
                  'Appliance "' + name + '" already exists in dictionary. '
                  'Please choose another name.')
            sys.exit()
        else:
            self[name] = _Appliance(name, path)

    def add_permanent_appliance(self, name, path):
        """
        Add an permanent appliance with the given parameters to the ApplianceDictionary.

        Parameters
        ----------
        name : str
            name of the permanent appliance

        path : str
            resource path to power consumption pattern data

        """
        if name in self:
            print(
                'Error: Permanent appliance was not initialized correctly. '
                'Appliance "' + name + '" already exists in dictionary. '
                'Please choose another name.')
            sys.exit()
        else:
            self[name] = _PermanentAppliance(name, path)


class _Appliance:
    def __init__(self, name, path, number=None, service=False):
        """
        Initialize an appliance with the given parameters.

        Parameters
        ----------
        name : str
            name of the appliance

        path : str
            resource path to power consumption pattern data

        number : int
            optional, default = None; number of power consumption patterns to be loaded from resource path

        service : bool
            optional, default = False; if True, a check is made to see if a service is
            available for the appliance at http://localhost:5555/
            and if so, energy data is loaded into that endpoint.
        """
        self.name = name
        self.path = path
        self.number = number
        self.power_consumption_pattern = pd.DataFrame()

        if service:
            try:
                self.data = self.get_data_from_service()
                print('--> using synthetic ' + str(self.name) + ' data')
            except:
                self.data = self.load_data()
                print('--> using real ' + str(self.name) + ' data')
        else:
            with open(self.path, 'rb') as fp:
                self.data = pickle.load(fp)
            print('--> ' + str(self.name) + ' data loaded')

        self.temp_pick_list = list(range(self.data.shape[0]))

    def is_appliance_in_use(self, time):
        """
        Check if the appliance is currently in use (above 0 watt).

        Parameters
        ----------
        time : int
            current second of the day, values from 0 to 86399

        Returns
        -------
        bool : boolean
            returns ground truth data of the resident in a
            pandas dataframe of shape (86400, 1)
        """
        try:
            value = self.power_consumption_pattern.loc[[time]].values[0][0]
            if value != 0:
                return True
            else:
                return False
        except KeyError:
            return False

    def get_data_from_service(self):
        """
        Get power consumption data from service.

        Returns
        -------
        bool : pandas dataframe
            returns power consumption data in a pandas dataframe of shape (number, max_pattern_lenght)
        """
        try:
            r = requests.post('http://localhost:5555/' + str(self.name), json={'number': self.number})
            data = pd.DataFrame.from_dict(r.json())
            data = pd.DataFrame(data.to_numpy())
            print('pulled ' + str(self.name) + ' data')
            return data
        except:
            print('failed pulling ' + str(self.name) + ' data')
            return self.data

    def load_data(self):
        """
        Load a number of power consumption patterns from the resource path.

        Returns
        -------
        bool : pandas dataframe
            returns power consumption data in a pandas dataframe of shape (number, max_pattern_lenght)
        """
        with open(self.path, 'rb') as fp:
            data = pickle.load(fp)
            if data.shape[0] > self.number:
                ## get x random samples of df
                data = data.sample(n=self.number)
        return data

    def pick_new_power_consumption_pattern(self):
        """
        Pull a new power consumption pattern from the loaded dataset and delete the pattern in the loaded dataset.
        If the dataset is empty, the data is reloaded from the resource path.

        Returns
        -------
        bool : pandas dataframe
            returns power consumption pattern in a pandas dataframe of shape (pattern_lenght, 1)
        """
        if not self.temp_pick_list:
            self.temp_pick_list = list(range(self.data.shape[0]))
        number = random.choice(self.temp_pick_list)
        self.temp_pick_list.remove(number)
        power_consumption_pattern = pd.DataFrame(self.data.iloc[number].transpose())
        return power_consumption_pattern

    def refresh_power_consumption_pattern(self):
        self.power_consumption_pattern = pd.DataFrame()


class _PermanentAppliance:
    def __init__(self, name, path):
        """
        Initialize a permanent appliance with the given parameters.

        Parameters
        ----------
        name : str
            name of the permanent appliance

        path : str
            resource path to power consumption pattern data
        """
        self.name = name
        self.filepath_list = glob.glob(path + '*.csv')
        self.temp_filepath_list = copy.deepcopy(self.filepath_list)
        self.random_filepath = ''
        self.data = pd.DataFrame()
        self.power_consumption_pattern = pd.DataFrame()
        print('--> ' + str(self.name) + ' data loaded')

    def refresh_power_consumption_pattern(self):
        """
        Pull a new power consumption pattern from the loaded dataset and delete the pattern in the loaded dataset.
        If the dataset is empty, the data is reloaded from the resource path.
        """
        if not self.temp_filepath_list:
            self.temp_filepath_list = copy.deepcopy(self.filepath_list)
        self.random_filepath = np.random.choice(self.temp_filepath_list, 1)[0]
        self.temp_filepath_list.remove(self.random_filepath)
        self.data = pd.read_csv(self.random_filepath, header=None)
        self.power_consumption_pattern = self.data
