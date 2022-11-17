import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from Utils.syntised_utils import save_action_sequence, create_directory
from Utils.actionsequence import ActionSequenceList
from Utils.appliance import ApplianceDictionary
from Utils.resident import ResidentDictionary


class SynTiSeD:
    def __init__(self, appliance_dict, permanent_appliance_dict, resident_dict, repetitions,
                 start_date='2000-01-01', save_path='./TimeSeriesData', variance=None, simulation_speed=20,
                 plot_data=False):
        self.appliance_dict = appliance_dict
        self.permanent_appliance_dict = permanent_appliance_dict
        self.resident_dict = resident_dict
        self.repetitions = repetitions
        self.start_date = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        self.save_path = save_path
        create_directory(save_path + "/")
        self.variance = variance
        if variance is not None:
            for key, resident in self.resident_dict.items():
                resident.variance(self.variance)
        self.simulation_speed = simulation_speed
        self.plot_data = plot_data

        self.simulation_time = 86400
        self.start_timestamp = self.start_date.timestamp()
        self.current_timestamp = self.start_timestamp
        self.used_appliance_list = list()

    def __build_energydata(self, time, permanent_energy_data):
        ## build energy data
        energy_data = pd.DataFrame()
        energy_data = pd.concat([energy_data, permanent_energy_data[:(time + 1)]], axis=1)

        for appliance in self.used_appliance_list:
            energy_data = pd.concat([energy_data, appliance.power_consumption_pattern[:(time+1)]], axis=1)

        energy_data.insert(0, 'smartMeter', energy_data.sum(axis=1))

        time_list = list()
        for i in range(time + 1):
            _time = datetime.fromtimestamp(i + self.current_timestamp)
            time_list.append(_time)
        time_df = pd.DataFrame(time_list)
        energy_data = pd.concat([energy_data, time_df.rename(columns={time_df.columns[0]: 'time'})], axis=1)
        energy_data.set_index(['time'], inplace=True)
        energy_data = energy_data.fillna(0)
        return energy_data

    def __step(self, second):
        for key, resident in self.resident_dict.items():
            ## check, if a new action beginns
            if second == resident.current_action_sequence[resident.action_seq_iterator].timestamp:
                action_name = resident.current_action_sequence[resident.action_seq_iterator].name
                ## check if there are energy data for the action
                if action_name in self.appliance_dict:
                    resident.next_appliances_to_activate.append(self.appliance_dict[action_name])
                    ## if yes, check if the appliance was used before
                    if self.appliance_dict[action_name] not in self.used_appliance_list:
                        ## if the appliance was not been used before, add it to the list
                        self.used_appliance_list.append(self.appliance_dict[action_name])
                ## increase the action sequence iterator of the avatar so we can proceed with the next action
                if resident.action_seq_iterator < len(resident.current_action_sequence) - 1:
                    resident.action_seq_iterator += 1

            resident.step(second)

    def __simulate_day(self, day):
        date_obj = datetime.fromtimestamp(self.current_timestamp).strftime('%Y-%m-%d')
        print('Start Simulation of Day ' + date_obj)

        ## Check if appliances of the previous day still consuming energy
        for appliance in list(self.used_appliance_list):
            energy_from_prev_day = appliance.power_consumption_pattern[(self.simulation_time+1):].reset_index(drop=True)
            sum_energy_consumption = sum(energy_from_prev_day.iloc[:, 0])
            if energy_from_prev_day.empty or sum_energy_consumption <= 0.0:
                self.used_appliance_list.remove(appliance)
                appliance.refresh_power_consumption_pattern()
            else:
                appliance.power_consumption_pattern = energy_from_prev_day

        ## refresh permanent Appliances
        for key, value in self.permanent_appliance_dict.items():
            value.refresh_power_consumption_pattern()

        ## refresh Residents
        saved_act_seq_list = []
        for key, resident in self.resident_dict.items():
            resident.pick_action_sequence_consecutively(day)
            saved_act_seq = save_action_sequence(resident.current_action_sequence, self.save_path, self.current_timestamp)
            saved_act_seq_list.append(saved_act_seq)

        ## Load Permanent Energy Data
        permanent_energy_data = pd.DataFrame()
        for key, value in self.permanent_appliance_dict.items():
            power_consumption_pattern = value.power_consumption_pattern[:self.simulation_time]
            power_consumption_pattern = power_consumption_pattern.rename(columns={power_consumption_pattern.columns[0]: value.name})
            permanent_energy_data = pd.concat([permanent_energy_data, power_consumption_pattern], axis=1)

        ## iterate over every second of the day, to check if there is a action scheduled
        for second in range(self.simulation_time):
            self.__step(second)

        ## build energy data
        energy_data_day = self.__build_energydata(self.simulation_time, permanent_energy_data)
        energy_data_day = energy_data_day.iloc[:self.simulation_time]
        energy_data_day = energy_data_day.round(3)
        energy_data_day.to_csv(self.save_path + '/' + date_obj + '.csv')
        print('Simulation of Day ' + date_obj + ' done!')
        self.current_timestamp = self.current_timestamp + self.simulation_time
        return energy_data_day, saved_act_seq_list

    def run_simulation(self):
        print(' ')
        for day in range(self.repetitions):
            energy_data_day, saved_act_seq_list = self.__simulate_day(day)
            if self.plot_data:
                plt.plot(energy_data_day)
                plt.show()
        sys.stdout.close()
        sys.exit()
        return energy_data_day, saved_act_seq_list


## Set parameters
simulated_days = 14
simulation_start_date = '2022-02-01'

## Initialize appliances
appl_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/'
appl_dict = ApplianceDictionary()
appl_dict.add_appliance('coffee machine', appl_resource_path + 'CoffeeMachine/df_zero_filled')
appl_dict.add_appliance('extractor fan', appl_resource_path + 'ExtractorFan/df_zero_filled')
appl_dict.add_appliance('kettle', appl_resource_path + 'Kettle/df_zero_filled')
appl_dict.add_appliance('lamp', appl_resource_path + 'Lamp/df_zero_filled')
appl_dict.add_appliance('microwave', appl_resource_path + 'Microwave/df_zero_filled')
appl_dict.add_appliance('television', appl_resource_path + 'Television/df_zero_filled')
appl_dict.add_appliance('washing machine', appl_resource_path + 'WashingMachine/df_zero_filled')
appl_dict.add_appliance('water pump', appl_resource_path + 'WaterPump/df_zero_filled')

## Initialize permanent appliances
perm_appl_dict = ApplianceDictionary()
perm_appl_dict.add_permanent_appliance('radio', appl_resource_path + 'Radio/')
perm_appl_dict.add_permanent_appliance('television receiver', appl_resource_path + 'TelevisionReceiver/')

## Initialize avatars
action_variance = 600
action_seq_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/Activities'
action_seq_list = ActionSequenceList()
action_seq_list.append_action_seq_folder(action_seq_resource_path)

res_dict = ResidentDictionary()
res_dict.add_resident('Karl', action_seq_list, action_variance)

## run SynTiSeD
syntised = SynTiSeD(appl_dict, perm_appl_dict, res_dict, simulated_days, simulation_start_date)
syntised.plot_data = True
energy_data_day, saved_act_seq_list = syntised.run_simulation()
