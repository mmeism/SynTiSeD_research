import matplotlib.pyplot as plt
import pickle
import pandas as pd
from datetime import datetime

from syntised_utils import ROOT_DIR


class Sequencer:
    def __init__(self, appliance_name, input_path, output_path, power_treshold, patience, minimal_power_treshhold):
        """
        Initialize a sequencer with the given parameters.

        Parameters
        ----------
        appliance_name : str
            name of the appliance to be sequenced

        input_path : str
            resource path to the file to be sequenced

        output_path : str
            path where the sequenced power consumption patterns and the action sequence txt file is stored

        power_treshold : int
            this defines the minimum wattage required for the appliance to be recognized as on and sequencing to start

        patience : int
            this defines how many time steps the wattage must be below the power_threshold
            to stop sequencing the power consumption pattern

        minimal_power_treshhold : int
            the highest wattage of the power consumption pattern must be at least this high for the pattern to be set
        """
        self.appliance_name = appliance_name
        self.input_path = input_path
        self.output_path = output_path
        self.power_treshold = power_treshold
        self.patience = patience
        self.minimal_power_treshhold = minimal_power_treshhold

        self.pc_series_list = []

    def sequence_input(self, dataframe):
        """
        Sequence given time series data from a dataframe to power consumption pattens.

        Parameters
        ----------
        dataframe : pandas dataframe
            dataframe where columns 'timestamp' and 'power' have to be included
        """
        i = 0
        max_length = 0
        recording = False
        df_power = pd.DataFrame(dataframe['power'])
        df_time = pd.DataFrame(df['timestamp'])
        while i < df_power.shape[0]:
            print(str(i) + '/' + str(df_power.shape[0]))
            series = pd.Series(dtype='float64')
            inserting_index = 0
            passive_in_a_row = 0
            if df_power.iloc[i, 0] > self.power_treshold:
                if not recording:
                    recording_time = datetime.fromtimestamp(1649800800 + i).strftime("%H:%M:%S")
                recording = True
                series._set_value(i - 1, 0)
                while recording and i < df_power.shape[0]:
                    print('Recordings: ' + str(inserting_index))
                    if passive_in_a_row <= self.patience:
                        if df_power.iloc[i, 0] <= self.power_treshold:
                            passive_in_a_row += 1
                        else:
                            passive_in_a_row = 0
                            inserting_index += 1
                        series._set_value(i, df_power.iloc[i, 0])
                        i += 1
                    else:
                        inserting_index += 1
                        series._set_value(i, 0)
                        recording = False
                if len(series) > max_length:
                    max_length = len(series)
                if series.max() > self.minimal_power_treshhold:
                    self.pc_series_list.append(series)
                    plt.plot(series)
                    file_object = open(self.appliance_name + '.txt', 'a')
                    day = df_time.iloc[i, 0].split(' ')[0]
                    file_object.write(day + ',"' + self.appliance_name + '",' + recording_time)
                    file_object.write("\n")
            else:
                i = i + 1

    def save_pc_patterns(self):
        """
        Save the list of power consumption patterns with pickle.
        """
        if self.pc_series_list:
            with open(self.output_path + self.appliance_name + '_pt' + str(self.power_treshold)
                      + '_pa' + str(self.patience) + '_mpt' + str(self.minimal_power_treshhold), 'wb') as fp:
                pickle.dump(self.pc_series_list, fp)
            print('Power consumption patterns saved.')
        else:
            print('Error: No sequenced power consumption patterns available to be saved.')


time_series_file = ROOT_DIR + '/Resources/ApplianceData/Example_seq_file.csv'

## Check data
df_plot = pd.read_csv(time_series_file)
plt.plot(df_plot['power'])
plt.show()

## sequencer
power_treshold = 2
patience = 10
min_power_treshold = 25
df = pd.read_csv(time_series_file)

sequencer = Sequencer('example_appliance', time_series_file, '', power_treshold, patience, min_power_treshold)
sequencer.sequence_input(df)
sequencer.save_pc_patterns()

## show sequenced power consumption patterns
with open('example_appliance_pt2_pa10_mpt25', 'rb') as fp:
    series_list = pickle.load(fp)
    for i in range(len(series_list)):
        series_list[i] = series_list[i].reset_index(drop=True)
        plt.plot(series_list[i])
        plt.title('pattern_' + str(i+1))
        plt.show()
