from SynTiSeD import SynTiSeD
from Utils.actionsequence import ActionSequenceList
from Utils.appliance import ApplianceDictionary
from Utils.resident import ResidentDictionary


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
