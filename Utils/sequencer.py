import pickle
import matplotlib.pyplot as plt
import pandas as pd

from syntised_utils import ROOT_DIR


class Sequencer:
    def __init__(self, appliance_name: str, input_path: str, output_path: str, power_threshold: int = 1,
                 patience: int = 10, minimal_power_threshold: int = 10, maximum_power_threshold: int = 20000,
                 minimal_pattern_lenght: int = 10, maximum_pattern_lenght: int = 3000,
                 total_power_consumption_threshold: int = 1000000):
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

        power_threshold : int
            the minimum wattage required for the appliance to be recognized as on and sequencing to start

        patience : int
            this defines how many time steps the wattage must be below the power_threshold
            to stop sequencing the power consumption pattern

        minimal_power_threshold : int
            the highest wattage per time step of the power consumption pattern must be at least this high
            for the pattern to be recorded

        maximum_power_threshold : int
            the highest wattage per time step of the power consumption pattern must not exceed this value
            for the pattern to be recorded

        minimal_pattern_lenght : int
            the power consumption pattern must have at least that number of time steps to be recorded

        maximum_pattern_lenght : int
            the power consumption pattern must not exceed the number that number of time steps to be recorded

        total_power_consumption_threshold : int
            the total power consumption of the whole pattern must not be higher than this value for the
            pattern to be recorded
        """
        self.appliance_name = appliance_name
        self.input_path = input_path
        self.output_path = output_path
        self.power_threshold = power_threshold
        self.patience = patience
        self.minimal_power_threshold = minimal_power_threshold
        self.maximum_power_threshold = maximum_power_threshold
        self.minimal_pattern_lenght = minimal_pattern_lenght
        self.maximum_pattern_lenght = maximum_pattern_lenght
        self.total_power_consumption_threshold = total_power_consumption_threshold

        self.pc_series_list = []

    def _state_ranges(self, Series, first_val_is_target=False):
        """
        returns pairs of indices of the input Series that are characterized by
        successive changes in value, and hence, could represent the starting- and
        endpoint of specific "states"

        for instance, if the input Series contains data with only two values,
        e.g. True/False or 1/0, representing the states of a device, and the index
        contains the timestamps of these states, this function returns pairs of
        timestamps representing the on- and offsets of these states. Whether these
        on- and offsets are returned for "on" or "off" states can be switched via
        the first_val_is_target parameter.

        Parameters
        ----------
        Series : pandas Series with Boolean or int/float values
        first_val_is_target : BOOL
            if True, the first sequence/pair of indices starts at the first index
            of Series (the first value in Series is assumed to be a "target" for
            which we seek the on- and offsets)

        Returns
        -------
        change_ind_pairs : LIST
            contains a list with one list of 2 indices for every "state" period
        """
        Seriesdiff = Series.diff()
        Seriesdiff.iloc[0] = first_val_is_target

        change_ind = Seriesdiff.loc[Seriesdiff == True].index

        def cut_into_pairs(x, last_ind):
            for ii in range(0, len(x), 2):
                try:
                    yield [x[ii], x[ii + 1]]
                except IndexError:
                    yield [x[ii], last_ind]

        change_ind_pairs = [*cut_into_pairs(change_ind, Series.index[-1])]

        return change_ind_pairs

    def _check_and_cut_sequences(self, df, sequence_windows):
        sequences = []
        for window in sequence_windows:
            sequence = df.loc[window[0]:window[-1], 'power']
            if self.minimal_power_threshold <= sequence.max() <= self.maximum_power_threshold \
                    and self.minimal_pattern_lenght <= sequence.size <= self.maximum_pattern_lenght \
                    and sequence.sum() <= self.total_power_consumption_threshold:
                sequences.append(sequence)
        return sequences

    def sequence_input(self, dataframe, plot: bool = False):
        """
        Sequence given time series data from a dataframe to power consumption pattens.

        Parameters
        ----------
        dataframe : pandas dataframe
            dataframe where columns 'timestamp' and 'power' have to be included
        plot : BOOL
            if True, plot sequences
        """
        df = dataframe.copy()
        df.timestamp = pd.to_datetime(df.timestamp)
        df = df.set_index('timestamp', drop=True)

        df['rolling_left'] = df['power'].rolling(f'{self.patience}s').max() > self.power_threshold
        df['rolling_right'] = df['power'][-1::-1].rolling(f'{self.patience}s').max()[-1::-1] > self.power_threshold
        df['toBeSequenced'] = df['rolling_left'] & df['rolling_right']

        sequence_windows = self._state_ranges(df['toBeSequenced'], df['toBeSequenced'][0])

        self.pc_series_list = self._check_and_cut_sequences(df, sequence_windows)

        for series in self.pc_series_list:
            if plot:
                plt.plot(series)

            file_object = open(f'{self.appliance_name}.txt', 'a')
            day = series.index[0].strftime('%Y-%m-%d')
            recording_time_start = series.index[0].strftime('%H:%M:%S')
            recording_time_end = series.index[-2].strftime('%H:%M:%S')
            file_object.write(f'{day},"{self.appliance_name}",{recording_time_start},{recording_time_end}')
            file_object.write("\n")

    def save_pc_patterns(self):
        """
        Save the list of power consumption patterns with pickle.
        """
        if self.pc_series_list:
            with open(f'{self.output_path}{self.appliance_name}_pt{self.power_threshold}_pa{self.patience}'
                      f'_pt{self.minimal_power_threshold}_{self.maximum_power_threshold}'
                      f'_pl{self.minimal_pattern_lenght}_{self.maximum_pattern_lenght}'
                      f'_tpc{self.total_power_consumption_threshold}', 'wb') as fp:
                pickle.dump(self.pc_series_list, fp)
            print('Power consumption patterns saved.')
        else:
            print('Error: No sequenced power consumption patterns available to be saved.')


if __name__ == '__main__':
    time_series_file = ROOT_DIR + '/Resources/ApplianceData/Example_seq_file.csv'

    ## Check data
    df = pd.read_csv(time_series_file)
    plt.plot(df['power'])
    plt.show()

    ## sequencer
    power_threshold = 2
    patience = 10
    min_power_threshold = 25
    max_power_threshold = 20000
    min_pattern_lenght = 10
    max_pattern_lenght = 43200
    total_power_consumption_threshold = 1000000  # in kwh umrechnen

    sequencer = Sequencer('example_appliance', time_series_file, '', power_threshold, patience, min_power_threshold,
                          max_power_threshold, min_pattern_lenght, max_pattern_lenght,
                          total_power_consumption_threshold)
    sequencer.sequence_input(df)
    sequencer.save_pc_patterns()

    ## show sequenced power consumption patterns
    with open(f'example_appliance_pt{power_threshold}_pa{patience}_pt{min_power_threshold}_{max_power_threshold}'
              f'_pl{min_pattern_lenght}_{max_pattern_lenght}_tpc{total_power_consumption_threshold}', 'rb') as fp:
        series_list = pickle.load(fp)
        for i in range(len(series_list)):
            series_list[i] = series_list[i].reset_index(drop=True)
            plt.plot(series_list[i])
            plt.title(f'pattern_{i+1}')
            plt.show()
