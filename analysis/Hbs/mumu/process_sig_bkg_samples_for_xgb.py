"""Build the *binary* (signal vs background) BDT training table from stage-1 ntuples.

Reads the flat ntuples for every process in ``mode_names``, turns each into a
pandas DataFrame of the ``train_vars`` features, then samples a
cross-section-weighted mixture: the H->bs signal is taken in full and each
background is scaled to its expected relative yield (efficiency x cross-section)
so the training set reflects the physical background composition. Rows are
tagged with ``sample``, ``isSignal`` (1 only for ``mumuH_Hbs``), a train/valid
split flag ``valid``, and a ``norm_weight``. The concatenated table is written to
``<pkl>/preprocessed.pkl`` for ``train_xgb.py``.

Cross sections come from the central FCC process dictionary
(``FCCee_procDict_winter2023_IDEA.json``), with the rare/FCNC signals assigned a
placeholder xsec of 1. Run with ``--Stage training`` (default) to prepare the
training pickle, or ``--Stage validation`` to prepare the analysis-sample
pickle; the ``--Mode`` / ``--Folds`` arguments are vestigial.
"""
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
#from config.common_defaults import deffccdicts
deffccdicts = "/cvmfs/fcc.cern.ch/FCCDicts"

def get_data_paths(cur_mode, data_path):
    """Return the list of stage-1 ROOT files for process ``cur_mode`` under ``data_path``."""
    path = f"{data_path}/{mode_names[cur_mode]}"
    return glob.glob(f"{path}/*.root")

def calculate_event_counts_and_efficiencies(cur_mode, files, vars_list):
    """Load ``files`` for one process and return (N_generated, DataFrame, efficiency).

    ``N_generated`` is summed from each file's ``eventsProcessed`` counter, the
    DataFrame holds the ``vars_list`` columns for all rows surviving stage-1, and
    the efficiency is ``len(df) / N_generated``.
    """
    N_events = sum([uproot.open(f)["eventsProcessed"].value for f in files])
    df = pd.concat((ut.get_df(f, vars_list) for f in files), ignore_index=True)
    eff = len(df) / N_events
    return N_events, df, eff

def update_dataframe_with_additional_info(df, cur_mode, sig):
    """Tag ``df`` with its ``sample`` name and a binary ``isSignal`` flag (1 iff ``cur_mode == sig``)."""
    df['sample'] = cur_mode
    df['isSignal'] = int(cur_mode == sig)
    return df

def calculate_BDT_input_numbers(mode_names, sig, df, eff, xsec, frac):
    """Compute how many rows to draw from each process for the training mixture.

    The signal contributes ``frac[sig] * len(df[sig])`` rows. Each background is
    scaled to its expected share of the total background yield,
    ``eff[mode]*xsec[mode] / sum_bkg(eff*xsec)``, relative to the signal count so
    the sampled mixture matches the physical background composition. Returns a
    dict of row counts keyed by process.
    """
    N_BDT_inputs = {}
    print(f"Calculating number of BDT inputs for {mode_names}")
    print(f"eff = {eff}")
    xsec_tot_bkg = sum(eff[mode] * xsec[mode] for mode in mode_names if mode != sig)
    for cur_mode in mode_names:
        N_BDT_inputs[cur_mode] = (int(frac[cur_mode] * len(df[cur_mode])) if cur_mode == sig else
                                  int(frac[cur_mode] * len(df[sig]) * (eff[cur_mode] * xsec[cur_mode] / xsec_tot_bkg)))
    return N_BDT_inputs

def split_data_and_update_dataframe(df, N_BDT_inputs, xsec, N_events, cur_mode):
    """Down-sample one process to its target size and add train/valid split + weight.

    Draws ``N_BDT_inputs[cur_mode]`` rows (fixed seed), assigns a 70/30
    train/validation split via the ``valid`` boolean column, and stores the
    per-event ``norm_weight = xsec / N_generated`` used for lumi scaling.
    """
    df = df.sample(n=N_BDT_inputs[cur_mode], random_state=1)
    df0, df1 = train_test_split(df, test_size=0.3, random_state=7)
    df.loc[df0.index, "valid"] = False
    df.loc[df1.index, "valid"] = True
    df.loc[df.index, "norm_weight"] = xsec[cur_mode] / N_events[cur_mode]
    return df

def save_data_to_pickle(dfsum, pkl_path):
    """Create ``pkl_path`` if needed and write the combined table to ``preprocessed.pkl``."""
    print("Writing output to pickle file")
    ut.create_dir(pkl_path)
    print(f"--->Preprocessed saved {pkl_path}/preprocessed.pkl")
    dfsum.to_pickle(f"{pkl_path}/preprocessed.pkl")

def get_procDict(procFile):
    """Load and return the FCC process dictionary (cross sections, event counts, ...).

    Accepts an http(s) URL (fetched over the network) or a filename; a bare
    filename is resolved under the CVMFS ``FCCDicts`` directory. Exits with code
    3 if a local file cannot be found.
    """
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
    """Re-key ``procDict`` from on-disk sample names to the short process keys.

    Uses the inverse of ``mode_names`` (sample name -> short key) so lookups can
    use keys like ``"mumuH_Hbs"``; entries with no known short key are kept
    under their original name.
    """
    # Reverse the mode_names dictionary
    reversed_mode_names = {v: k for k, v in mode_names.items()}

    updated_dict = {}
    for key, value in procDict.items():
        new_key = reversed_mode_names.get(key, key)
        updated_dict[new_key] = value
    return updated_dict


def run(modes, n_folds, stage):
    """Build and write the binary BDT training/validation table for all processes.

    Resolves cross sections (from the process dict, with hard-coded values for
    the SM Higgs decays and placeholder=1 for the rare signals), then for every
    process in ``mode_names`` loads its ntuples, tags them, samples the
    cross-section-weighted mixture and adds the train/valid split, and finally
    concatenates everything and pickles it. ``stage`` selects the input/output
    location: "training" uses ``loc.TRAIN``/``loc.PKL``, otherwise the analysis
    samples ``loc.ANALYSIS``/``loc.PKL_Val``. ``modes`` and ``n_folds`` are unused.
    """

    procFile = "FCCee_procDict_winter2023_IDEA.json"
    proc_dict = get_procDict(procFile)
    procDict = update_procDict_keys(proc_dict, mode_names)

    xsec = {key: value["crossSection"] for key, value in procDict.items() if key in mode_names}

    # Standard SM Higgs decay channels
    xsec["mumuH_Hbb"] = 3.940000000
    xsec["mumuH_Hcc"] = 0.195600000
    xsec["mumuH_Hss"] = 0.001624000
    # xsec["mumuH_Huu"] = 0.000000609
    # xsec["mumuH_Hdd"] = 0.000001421

    #Off diagonals and rare signals
    xsec["mumuH_Hbs"] = 1
    xsec["mumuH_Hbd"] = 1
    xsec["mumuH_Hcu"] = 1
    xsec["mumuH_Hsd"] = 1
    xsec["mumuH_Huu"] = 1
    xsec["mumuH_Hdd"] = 1

    #print(f"Cross sections = {xsec}")
    
    sig = "mumuH_Hbs"
    data_path = loc.TRAIN if stage == "training" else loc.ANALYSIS
    pkl_path = loc.PKL if stage == "training" else loc.PKL_Val

    files = {}
    df = {}
    N_events = {}
    eff = {}
    vars_list = train_vars.copy()

    frac = {
        # Off-Diagonal Higgs Decays (FCNC Signals)
        "mumuH_Hbs":    1.0,
        "mumuH_Hbd":    1.0,
        "mumuH_Hcu":    1.0,
        "mumuH_Hsd":    1.0,

        # Diagonal Higgs Decays
        "mumuH_Hbb":    1.0,
        "mumuH_Hss":    1.0,
        "mumuH_Hcc":    1.0,
        "mumuH_Hdd":    1.0,
        "mumuH_Huu":    1.0,

        # Standard Model Backgrounds
        "mumuH":        1.0,
        "ZZ":           1.0,
        "WW":           1.0,
        "Zll":          1.0,
        "egamma":       1.0,
        "gammae":       1.0,
        "gaga_mumu":    1.0
    }

    for cur_mode in mode_names:
        files[cur_mode] = get_data_paths(cur_mode, data_path)
        N_events[cur_mode], df[cur_mode], eff[cur_mode] = calculate_event_counts_and_efficiencies(cur_mode, files[cur_mode], vars_list)
        print(f"Number of events in {cur_mode} = {N_events[cur_mode]}")
        print(f"Efficiency of {cur_mode} = {eff[cur_mode]}")
        df[cur_mode] = update_dataframe_with_additional_info(df[cur_mode], cur_mode, sig)

    N_BDT_inputs = calculate_BDT_input_numbers(mode_names, sig, df, eff, xsec, frac)

    print(f"Number of BDT inputs = {N_BDT_inputs}")
    for cur_mode in mode_names:
        df[cur_mode] = split_data_and_update_dataframe(df[cur_mode], N_BDT_inputs, xsec, N_events, cur_mode)

    dfsum = pd.concat([df[cur_mode] for cur_mode in mode_names])

    save_data_to_pickle(dfsum, pkl_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process mumuH, WWmumu, ZZ, Zll,eeZ MC to make reduced files for xgboost training')
    parser.add_argument("--Mode", action="store", dest="modes", default=["mumuH", "ZZ", "WWmumu", "Zll", "egamma", "gammae", "gaga_mumu"], help="Decay mode")
    parser.add_argument("--Folds", action="store", dest="n_folds", default=2, help="Number of Folds")
    parser.add_argument("--Stage", action="store", dest="stage", default="training", choices=["training", "validation"], help="training or validation")
    args = vars(parser.parse_args())
    run(**args)