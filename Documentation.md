# API reference
This document gives an overview of all SynTiSeD classes, functions and methods.
Date: Nov 17, 2022


* [Input formats](#input-formats)
  + [Time Series Data File](#time-series-data-file)
  + [Sequenced Power Consumption Patterns](#sequenced-power-consumtion-patterns)
  + [Action Sequence File](#action-sequence-file)
* [Classes](#classes)
  + [SynTiSeD](#synTiSeD)
  + [ResidentDictionary](#ResidentDictionary)
  + [Resident](#resident)
  + [ApplianceDictionary](#ApplianceDictionary)
  + [Appliance](#appliance)
  + [ActionSequenceList](#actionSequenceList)
  + [ActionSequence](#actionSequence)
  + [Action](#action)
  + [Sequencer](#sequencer)


-------
-------

# Input Formats
In the following there are the Input formats described for using SynTiSeD.

## Time Series Data File
A file that can be used by the [Sequencer](#sequencer) class exists in csv format and consists of the two columns 'timestamp' and 'power'.  
An example time series appears as follows and can also be found [here](https://github.com/mmeism/SynTiSeD_research/blob/main/Resources/ApplianceData/Example_seq_file.csv):

> timestamp,power  
> 2020-03-17 09:30:00,0.0  
> 2020-03-17 09:30:01,0.0  
> 2020-03-17 09:30:02,0.0  
> ...  

The csv file can also contain other columns, it's just important that there are two of them, named 'timestamp' and 'power'. The timestamps must be available in a constant frequency.

-------

## Sequenced Power Consumption Patterns
Sequence of n values, where n is the length of the energy consumption pattern.

-------

## Action Sequence File
An action sequence file (.txt file) consists of a sequence of individual actions, which in turn consist of 3 or 4 parameters (name, time, probability, variance(optional)) separated by a ','.  
An example action appears as follows and can also be found [here](https://github.com/mmeism/SynTiSeD_research/blob/main/Resources/ApplianceData/GeLaP_data/hh_04/Activities/2020-01-04.txt):

> "coffee machine", 07:39:55, 1, 600  

- `"coffee machine"`: **name** of the appliance that will be switched on; can have any name
- `07:39:55`: **timestamp** when the appliance is to be switched on; must be in Format hour:minute:second
- `1`: **probability** if this action will happen; must be a float number p (0<=p<=1), where 0 is 0% likely and 1 is 100% likely
- `600`: optional; **variance** in seconds that affects the timestamp of the action; the variance v spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.


It is important that the txt file only contains one action in one line, otherwise the file cannot be loaded. The individual actions can also be swapped in time in the txt file, SynTiSeD sorts the actions when loading.


-------
-------

# Classes
In the following there are the Classes described in more detail for using SynTiSeD.

## SynTiSeD
*class* SynTiSeD.[SynTiSeD](https://github.com/mmeism/SynTiSeD_research/blob/main/SynTiSeD.py#L13-L127) ()  
Simulates time series data,

### Parameters
* **appliances_dict**: ApplianceDictionary  
  dictionary with Appliances
* **resident_dict**: ResidentDictionary  
  dictionary with Residents
* **repetitions**: int  
  ...

### Methods
* **simulate_day**:   
  simulate one day with the given parameters  
* **run_simulation**:   
  run whole simulation  


### Examples
Initialize SynTiSeD with all the necessary parameters and run a simulation.
```ruby
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
```

-------

## ResidentDictionary
*class* Utils.resident.[ResidentDictionary](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/resident.py#L7-L34) (dict)  
Inherits from the dictionary class. Initialize a ResidentDictionary from dict.  

### Methods
* **add_resident**:   
  Add an resident with the given parameters to the ResidentDictionary.  
  + **Parameters**: 
    - **name**: str  
      name of the resident
    - **actionSequenceList**: ActionSequenceList  
        list of ActionSequences according to which the resident can act
    - **variance**: int  
      optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.

### Examples
Initialize an ActionSequenceList and an ResidentDictionary and add a resident.
```ruby
action_seq_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/Activities/'
action_seq_list = ActionSequenceList()
action_seq_list.append_action_seq('Seq_1', action_seq_resource_path + '2020-01-04.txt')
action_seq_list.append_action_seq('Seq_2', action_seq_resource_path + '2020-01-05.txt', 300)

res_dict = ResidentDictionary()
res_dict.add_resident('Karl', action_seq_list)
```

-------

## Resident
*class* Utils.resident.[\_Resident](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/resident.py#L37-L135) (name=None, action_sequences_list=None, variance=None)  
Initialize a resident with the given parameters

### Parameters
* **name**: str  
  name of the resident
* **action_sequences_list**: ActionSequenceList  
  list of ActionSequences according to which the resident can act
* **variance**: int  
  optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.

### Examples
Initialize an Resident.
```ruby
action_seq_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/Activities/'
action_seq_list = ActionSequenceList()
action_seq_list.append_action_seq('Seq_1', action_seq_resource_path + '2020-01-04.txt')
action_seq_list.append_action_seq('Seq_2', action_seq_resource_path + '2020-01-05.txt', 300)

example_resident = _Resident('Karl', action_seq_list, 600)
```

-------

## ApplianceDictionary
*class* Utils.appliance.[ApplianceDictionary](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/appliance.py#L11-L56) (dict)  
Inherits from the dictionary class. Initialize a ApplianceDictionary from dict.  

### Methods
* **add_appliance**:   
  Add an appliance with the given parameters to the ApplianceDictionary.  
  + **Parameters**: 
    - **name**: str  
      name of the appliance
    - **path**: str  
      resource path to power consumption pattern data

### Examples
Initialize an ApplianceDictionary and add some appliances.
```ruby
appl_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/'
appl_dict = ApplianceDictionary()
appl_dict.add_appliance('coffee machine', appl_resource_path + 'CoffeeMachine/df_zero_filled')
appl_dict.add_appliance('extractor fan', appl_resource_path + 'ExtractorFan/df_zero_filled')
```

-------

## Appliance
*class* Utils.appliance.[\_Appliance](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/appliance.py#L59-L176) (name=None, resourcePath=None)
Initialize an appliance with the given parameters.

### Parameters
* **name**: str  
  name of the appliance
* **resourcePath**: str  
  resource path to power consumption pattern data
* **number**: int  
  number of power consumption patterns to be loaded from resource path
* **service**: bool  
  default False; if True, a check is made to see if a service is available for the appliance at http://localhost:5555/ and if so, energy data is loaded into that endpoint.

### Methods
* **get_pattern**:   
  + **Parameters**  
    - **name**: str  
      ...

### Examples
Initialize an Appliance.
```ruby
appl_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/'
example_appliance = _Appliance('kettle', appl_resource_path + 'Kettle/df_zero_filled')
```

-------

## ActionSequenceList 
*class* Utils.actionsequence.[ActionSequenceList](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/actionsequence.py#L6-L44) (list)  
Inherits from the list class. Initialize an list of ActionSequence from list.
    
### Methods
* **append_action_seq**:
  + **Parameters**  
    - **name**: str  
      name of the action sequence
    - **resourcePath**: str  
      resource path to the action sequence
    - **variance**: int  
      optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.

* **append_action_seq_folder**:   
  + **Parameters**  
    - **resourcePath**: str  
      resource path to the action sequence
    - **variance**: int  
      optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.

### Examples
Initialize an ActionSequenceList.
```ruby
action_seq_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/Activities/'
action_seq_list = ActionSequenceList()
```
Append action sequences with different variances to the initialized ActionSequenceList.
```ruby
action_seq_list.append_action_seq('Seq_1', action_seq_resource_path + '2020-01-04.txt')
action_seq_list.append_action_seq('Seq_2', action_seq_resource_path + '2020-01-05.txt', 300)
action_seq_list.append_action_seq('Seq_3', action_seq_resource_path + '2020-01-06.txt', 200)
```
Append a folder of action sequences to the initialized ActionSequenceList.
```ruby
action_seq_list.append_action_seq_folder(action_seq_resource_path)
```

-------

## ActionSequence 
*class* Utils.actionsequence.[\_ActionSequence](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/actionsequence.py#47-L106) (name=None, path=None, variance=None)  
Inherits from the list class. Initialize an ActionSequence with the given parameters.

### Parameters
* **name**: str  
  name of the action sequence
* **path**: str  
  resource path to the action sequence
* **variance**: int, optional
  optional; variance parameter in seconds; for each appliance, the variance spans an interval with zero, in which a value is randomly selected, that is added or subtracted to the timestamp of the action.


### Examples
Initialize an ActionSequence with and without the variance parameter.
```ruby
action_seq_resource_path = './Resources/ApplianceData/GeLaP_Data/hh_04/Activities/'
example_action_sequence = _ActionSequence('act_seq', action_seq_resource_path + '2020-01-04.txt')
example_action_sequence_1 = _ActionSequence('act_seq_1', action_seq_resource_path + '2020-01-05.txt', 400)
```

-------

## Action
*class* Utils.actionsequence.[\_Action](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/actionsequence.py#L109-L132) (name=None, timestamp=None, probability=None, variance=0)  
Initialize an action with the given parameters.

### Parameters
* **name**: str  
  Explanaition
* **timestamp**: str  
  Explanaition
* **probability**: float  
  Explanaition
* **variance**: int, optional, default=0  
  Explanaition

### Examples
Initialize an Action with and without the variance parameter.
```ruby
example_action = _Action('kettle', 6980, 1.0)
example_action_1 = _Action('microwave', 40710, 0.8, 600)
```

-------

## Sequencer
*class* Utils.sequencer.[Sequencer](https://github.com/mmeism/SynTiSeD_research/blob/main/Utils/sequencer.py#L10-L105) (appliance_name=None, input_path=None, output_path=None, power_treshold=None, patience=None, minimal_power_treshhold=None )  

Initialize a sequencer with the given parameters.

### Parameters
* **appliance_name**: str  
  name of the appliance to be sequenced
* **input_path**: str  
  resource path to the file to be sequenced
* **output_path**: str  
  path where the sequenced power consumption patterns and the action sequence txt file is stored
* **power_treshold**: int  
  this defines the minimum wattage required for the appliance to be recognized as on and sequencing to start
* **patience**: int  
  this defines how many time steps the wattage must be below the power_threshold to stop sequencing the power consumption pattern
* **minimal_power_treshhold**: int  
  the highest wattage of the power consumption pattern must be at least this high for the pattern to be set

### Methods
* **sequence_input**:  
  Sequence given time series data from a dataframe to power consumption pattens  
  + **Parameters**: 
    - **dataframe**: pandas dataframe  
      dataframe where columns 'timestamp' and 'power' have to be included

### Examples
Initialize a Sequencer, sequence power consumption patterns out of time series data file and save them.
```ruby
power_treshold = 2
patience = 10
min_power_treshold = 25
df = pd.read_csv(time_series_file)

sequencer = Sequencer('example_appliance', time_series_file, '', power_treshold, patience, min_power_treshold)
sequencer.split_into_pc_patterns(df)
sequencer.save_pc_patterns()
```

