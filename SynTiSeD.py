import sys
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from SynTiSeD.Utils.syntised_utils import save_action_sequence, create_directory, save_apl_active_phases


class SynTiSeD:
    def __init__(self, appliance_dict, permanent_appliance_dict, resident_dict,
                 repetitions: int, start_date: str = '2000-01-01', save_path: str = './TimeSeriesData',
                 variance: int = None, simulation_speed: int = 20, plot_data: bool = False,
                 save_active_phases: bool = False):
        self.appliance_dict = appliance_dict
        self.permanent_appliance_dict = permanent_appliance_dict
        self.resident_dict = resident_dict
        self.repetitions = repetitions
        self.start_date = datetime.strptime(f'{start_date.strip()}+00:00', "%Y-%m-%d%z")
        self.save_path = save_path
        create_directory(f'{save_path}/ActionSeq/')
        create_directory(f'{save_path}/ActionSeq_active_phases/')
        self.variance = variance
        if variance is not None:
            for key, resident in self.resident_dict.items():
                resident.variance(self.variance)
        self.simulation_speed = simulation_speed
        self.plot_data = plot_data
        self.save_active_phases = save_active_phases

        self.simulation_time = 86400
        self.start_timestamp = self.start_date.timestamp()
        self.current_timestamp = self.start_timestamp
        self.used_appliance_list = list()

    def __build_energydata(self, time: int, permanent_energy_data):
        ## build energy data
        energy_data = pd.DataFrame(np.empty((time, 0)))
        energy_data = pd.concat([energy_data, permanent_energy_data[:time]], axis=1)

        for appliance in self.used_appliance_list:
            energy_data = pd.concat([energy_data, appliance.power_consumption_pattern[:time]], axis=1)

        energy_data.insert(0, 'smartMeter', energy_data.sum(axis=1))

        energy_data.index = pd.to_datetime(energy_data.index, unit='s', origin=datetime.utcfromtimestamp(self.current_timestamp))
        energy_data.index.name = 'timestamp'
        energy_data = energy_data.fillna(0)
        return energy_data

    def __step(self, second: int):
        for key, resident in self.resident_dict.items():
            ## check, if a new action beginns
            if resident.action_seq_iterator < len(resident.current_action_sequence) and \
                    second == resident.current_action_sequence[resident.action_seq_iterator].start_timestamp:
                action_name = resident.current_action_sequence[resident.action_seq_iterator].name
                ## check if there are energy data for the action
                if action_name in self.appliance_dict:
                    resident.next_appliances_to_activate.append(self.appliance_dict[action_name])
                    ## if yes, check if the appliance was used before
                    if self.appliance_dict[action_name] not in self.used_appliance_list:
                        ## if the appliance was not been used before, add it to the list
                        self.used_appliance_list.append(self.appliance_dict[action_name])
                ## increase the action sequence iterator of the resident
                resident.action_seq_iterator += 1

            resident.step(second)

    def __simulate_day(self, day: int):
        date_obj = datetime.utcfromtimestamp(self.current_timestamp).strftime('%Y-%m-%d')
        print(f'Start Simulation of Day {date_obj}')

        ## Check if appliances of the previous day still consuming energy
        for appliance in list(self.used_appliance_list):
            energy_from_prev_day = appliance.power_consumption_pattern[(self.simulation_time+1):].reset_index(drop=True)
            if energy_from_prev_day.empty or sum(energy_from_prev_day.iloc[:, 0]) <= 0.0:
                self.used_appliance_list.remove(appliance)
                appliance.refresh_power_consumption_pattern()
            else:
                appliance.power_consumption_pattern = energy_from_prev_day

        ## refresh permanent Appliances
        for key, value in self.permanent_appliance_dict.items():
            value.refresh_power_consumption_pattern()

        ## refresh Residents
        for key, resident in self.resident_dict.items():
            resident.pick_action_sequence_consecutively(day)

        ## Load Permanent Energy Data
        permanent_energy_data = pd.DataFrame()
        for key, value in self.permanent_appliance_dict.items():
            power_consumption_pattern = value.power_consumption_pattern[:self.simulation_time]
            power_consumption_pattern = power_consumption_pattern.rename(columns={power_consumption_pattern.columns[0]: value.name})
            permanent_energy_data = pd.concat([permanent_energy_data, power_consumption_pattern], axis=1)

        ## iterate over every second of the day, to check if there is a action scheduled
        for second in range(self.simulation_time):
            self.__step(second)

        ## save action sequence ground truth
        for key, resident in self.resident_dict.items():
            save_path = save_action_sequence(resident.current_action_sequence, self.save_path, self.current_timestamp)
            if self.save_active_phases:
                save_apl_active_phases(save_path, '')

        ## build energy data
        energy_data_day = self.__build_energydata(self.simulation_time, permanent_energy_data)
        energy_data_day = energy_data_day.iloc[:self.simulation_time]
        energy_data_day = energy_data_day.round(3)
        energy_data_day.to_csv(f'{self.save_path}/{date_obj}.csv')
        print(f'Simulation of Day {date_obj} done!')
        self.current_timestamp = self.current_timestamp + self.simulation_time
        return energy_data_day

    def run_simulation(self):
        print(' ')
        for day in range(self.repetitions):
            energy_data_day = self.__simulate_day(day)
            if self.plot_data:
                plt.plot(energy_data_day)
                plt.show()
        sys.stdout.close()
        sys.exit()
        return energy_data_day


