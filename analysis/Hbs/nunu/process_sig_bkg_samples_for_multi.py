import os
import sys
import argparse
import glob
import uproot
import pandas as pd
from sklearn.model_selection import train_test_split
from userConfig import loc, train_vars, mode_names
import utils as ut
import json
from tqdm import tqdm
#from config.common_defaults import deffccdicts
deffccdicts = "/cvmfs/fcc.cern.ch/FCCDicts"

def get_data_paths(cur_mode, data_path):
    path = f"{data_path}/{mode_names[cur_mode]}"
    return glob.glob(f"{path}/*.root")

def calculate_event_counts_and_efficiencies(cur_mode, files, vars_list):
    if not files:
        raise FileNotFoundError(
            f"No ROOT files found for mode: '{cur_mode}'."
        )
    total_events = 0
    dfs = []
    
    for f in tqdm(files, desc=f"Loading {cur_mode}", leave=False):
        with uproot.open(f) as root_file:
            total_events += root_file["eventsProcessed"].value
        df_file = ut.get_df(f, vars_list)
        dfs.append(df_file)

    df = pd.concat(dfs, ignore_index=True)
    eff = len(df) / total_events if total_events > 0 else 0
    
    return total_events, df, eff

def update_dataframe_with_additional_info(df, cur_mode, class_mapping):
    df = df.copy()
    df["sample"] = cur_mode

    if cur_mode not in class_mapping:
        raise KeyError(f"No class label defined for mode: {cur_mode}")

    df["label"] = class_mapping[cur_mode]
    return df

def calculate_multiclass_BDT_input_numbers(mode_names, df, eff, xsec, class_mapping, frac):
    print("Calculating 3-class BDT inputs using cross-section proportions...")

    # Calculate the total physical "weight" (yield) for each class
    class_xsec_totals = {0: 0, 1: 0, 2: 0, 3:0, 4:0, 5:0, 6:0, 7:0}
    for cur_mode in mode_names:
        c = class_mapping[cur_mode]
        # Yield is proportional to efficiency * cross-section
        class_xsec_totals[c] += eff[cur_mode] * xsec[cur_mode]

    class_avail_counts = {0: 0, 1: 0, 2: 0, 3:0, 4:0, 5:0, 6:0, 7:0}
    for cur_mode in mode_names:
        c = class_mapping[cur_mode]
        class_avail_counts[c] += len(df[cur_mode])
        
    # Pick the smallest class size as our target budget for ALL three classes
    max_events_per_class = min(class_avail_counts.values())
    print(f"--> Target size for each class: {max_events_per_class} events")

    # Distribute the budget inside each class using cross-section ratios
    N_BDT_inputs = {}
    for c_target in [6,7]:
        #For each group, create a list of the modes in that group
        modes_in_class = [m for m in mode_names if class_mapping[m] == c_target]
        
        for cur_mode in modes_in_class:
            # What percentage of this class's physical cross-section does this mode represent?
            if class_xsec_totals[c_target] > 0:
                #Fraction of yield for that mode/ total yield of the group
                mode_fraction_of_class = (eff[cur_mode] * xsec[cur_mode]) / class_xsec_totals[c_target]
            else:
                mode_fraction_of_class = 1.0 / len(modes_in_class) # Fallback if xsec is 0
            
            # Calculate the allocation
            #Multiply the fraction by the events in group and frac (usually 1)
            allocated_events = int(max_events_per_class * mode_fraction_of_class * frac[cur_mode])
            
            # Safety check: ensure we don't request more rows than exist in df for this mode
            if allocated_events > len(df[cur_mode]):
                print(f"Warning: More events requested than exist for {cur_mode} ({allocated_events} requested vs {len(df[cur_mode])} available)")

            N_BDT_inputs[cur_mode] = min(allocated_events, len(df[cur_mode]))
    
    for c_target in [0,1,2,3,4,5]:

        modes_in_class = [m for m in mode_names if class_mapping[m] == c_target]
        
        for cur_mode in modes_in_class:
            #Fraction for each decay
            mode_fraction_of_class = 1.0/len(modes_in_class)

            #Multiply the fraction by the events in group and frac (usually 1)
            allocated_events = int(max_events_per_class * mode_fraction_of_class * frac[cur_mode])
            
            # Safety check: ensure we don't request more rows than exist in df for this mode
            if allocated_events > len(df[cur_mode]):
                print(f"Warning: More events requested than exist for {cur_mode} ({allocated_events} requested vs {len(df[cur_mode])} available)")

            N_BDT_inputs[cur_mode] = min(allocated_events, len(df[cur_mode]))
            
    return N_BDT_inputs

def split_data_and_update_dataframe(df, N_BDT_inputs, xsec, N_events, cur_mode):
    df = df.sample(n=N_BDT_inputs[cur_mode], random_state=1)
    df0, df1 = train_test_split(df, test_size=0.3, random_state=7)
    df.loc[df0.index, "valid"] = False
    df.loc[df1.index, "valid"] = True
    df.loc[df.index, "norm_weight"] = xsec[cur_mode] / N_events[cur_mode]
    return df

def save_data_to_pickle(dfsum, pkl_path):
    print("Writing output to pickle file")
    ut.create_dir(pkl_path)
    print(f"--->Preprocessed saved {pkl_path}/preprocessed.pkl")
    dfsum.to_pickle(f"{pkl_path}/preprocessed.pkl")

def get_procDict(procFile):
    procDict = None
    if 'http://' in procFile or 'https://' in procFile:
        print ('----> getting process dictionary from the web')
        import urllib.request
        req = urllib.request.urlopen(procFile).read()
        procDict = json.loads(req.decode('utf-8'))
    else:
        if not ('eos' in procFile): 
            #procFile = os.path.join(os.getenv('FCCDICTSDIR', deffccdicts), '') + procFile
            procFile = "/cvmfs/fcc.cern.ch/FCCDicts/" + procFile
        print(procFile)
        if not os.path.isfile(procFile):
            print ('----> No procDict found: ==={}===, exit'.format(procFile))
            sys.exit(3)
        with open(procFile, 'r') as f:
            procDict=json.load(f)

    return procDict

def update_procDict_keys(procDict, mode_names):
    # Reverse the mode_names dictionary
    reversed_mode_names = {v: k for k, v in mode_names.items()}

    updated_dict = {}
    for key, value in procDict.items():
        new_key = reversed_mode_names.get(key, key)
        updated_dict[new_key] = value
    return updated_dict

    
def run(modes, n_folds, stage):

    procFile = "FCCee_procDict_winter2023_IDEA.json"
    proc_dict = get_procDict(procFile)
    procDict = update_procDict_keys(proc_dict, mode_names)

    xsec = {key: value["crossSection"] for key, value in procDict.items() if key in mode_names} 

    #edited cross sections
    xsec["nunuH_HZa"] = 0.01
    xsec["nunuH_Hgg"] = 0.01 #0.0005538
    xsec["nunuH_Hss"] = 0.01 #0.001624000

    #Off diagonals and rare signals (generated)
    xsec["nunuH_Hbs"] = 1
    xsec["nunuH_Hbd"] = 1
    xsec["nunuH_Hcu"] = 1
    xsec["nunuH_Hsd"] = 1
    xsec["nunuH_Huu"] = 1
    xsec["nunuH_Hdd"] = 1

    print(f"Cross sections = {xsec}")
    
    data_path = loc.TRAIN if stage == "training" else loc.ANALYSIS
    pkl_path = loc.PKL if stage == "training" else loc.PKL_Val

    files = {}
    df = {}
    N_events = {}
    eff = {}
    vars_list = train_vars.copy()

    frac = {mode: 1.0 for mode in mode_names}

    class_mapping = {

        # Class 0 (Hbs)
        "nunuH_Hbs":    0,

        # Classes for each rare decay
        "nunuH_Huu":    1,
        "nunuH_Hdd":    2,
        "nunuH_Hcu":    3,
        "nunuH_Hsd":    4,
        "nunuH_Hbd":    5,

        "nunuH":        6,  # Inclusive ZH
        "nunuH_Hbb":    6,
        "nunuH_Hcc":    6,
        "nunuH_Hss":    6,
        "nunuH_Hgg":    6,
        "nunuH_HWW":    6,
        "nunuH_HZZ_noInv":    6,
        "nunuH_HZa":    6,
        "nunuH_Htautau":    6,

        # Class 3
        "ZZ":           7, #eeZZ
        "WW":           7, #eeWW
        "Zqq":          7,
        "nuenueZ":      7,
    }

    for cur_mode in mode_names:
        files[cur_mode] = get_data_paths(cur_mode, data_path)
        #For each mode, retrieve the number of events, the data for each event, and the percentage of events remaining after the cut
        N_events[cur_mode], df[cur_mode], eff[cur_mode] = calculate_event_counts_and_efficiencies(cur_mode, files[cur_mode], vars_list)
        print(f"Number of events in {cur_mode} = {N_events[cur_mode]}")
        print(f"Efficiency of {cur_mode} = {eff[cur_mode]}")
        #Label each mode with its group for multiclass
        df[cur_mode] = update_dataframe_with_additional_info(df[cur_mode], cur_mode, class_mapping)

    #Properly divides each group by cross section, keeping rare decays equal
    N_BDT_inputs = calculate_multiclass_BDT_input_numbers(mode_names, df, eff, xsec, class_mapping, frac)

    print(f"Number of BDT inputs = {N_BDT_inputs}")
    for cur_mode in mode_names:
        df[cur_mode] = split_data_and_update_dataframe(df[cur_mode], N_BDT_inputs, xsec, N_events, cur_mode)

    dfsum = pd.concat([df[cur_mode] for cur_mode in mode_names])

    save_data_to_pickle(dfsum, pkl_path)

if __name__ == '__main__':
    #As far as I can tell only --stage does anything here, tbh none of these are useful and have been phased out
    parser = argparse.ArgumentParser(description='Process nunuH, WWnunu, ZZ, Zll,eeZ MC to make reduced files for xgboost training')
    parser.add_argument("--Mode", action="store", dest="modes", default=["nunuH", "ZZ", "WWnunu", "Zll", "egamma", "gammae", "gaga_nunu"], help="Decay mode")
    parser.add_argument("--Folds", action="store", dest="n_folds", default=2, help="Number of Folds")
    parser.add_argument("--Stage", action="store", dest="stage", default="training", choices=["training", "validation"], help="training or validation")
    args = vars(parser.parse_args())
    run(**args)