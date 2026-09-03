"""Train the *binary* (signal vs background) XGBoost classifier.

Reads the preprocessed training table (``<pkl>/preprocessed.pkl`` from
``process_sig_bkg_samples_for_xgb.py``), splits it into train/validation sets by
the ``valid`` flag, fits an ``XGBClassifier`` on the ``train_vars`` features with
``isSignal`` as target, and saves the model both as a TMVA-compatible ROOT file
(``BDT/xgb_bdt.root``, for RDataFrame inference in the stage-1 producers) and as
a joblib pickle (``BDT/xgb_bdt.joblib``, for ``evaluation.py``). Run directly:
``python train_xgb.py``.
"""
import os
import sys
import argparse
import json
import glob

import numpy as np
import pandas as pd
import xgboost as xgb
import uproot
import ROOT
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rc

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import accuracy_score
from sklearn.utils.class_weight import compute_sample_weight

from userConfig import loc, train_vars, mode_names
#import plotting
import utils as ut

rc('font', **{'family': 'serif', 'serif': ['Roman']})
rc('text', usetex=True)


def run():
    """Load the training table, fit the binary BDT and save it. The script entry point."""

    modes = ["mumuH_Hbs", "mumuH_Hbd", "mumuH_Hcu", "mumuH_Hsd",
        "mumuH_Hbb", "mumuH_Hss", "mumuH_Hcc", "mumuH_Hdd", "mumuH_Huu",
        "mumuH", "ZZ", "WW", "Zll", "egamma", "gammae", "gaga_mumu"]
        
    vars_list = train_vars
    print("TRAINING VARS")
    print(vars_list)
    path = f"{loc.PKL}"
    df = pd.read_pickle(f"{path}/preprocessed.pkl")

    print_stats(df, modes)

    X_train, y_train, X_valid, y_valid = split_data(df, vars_list)

    config_dict = get_config_dict()
    early_stopping_round = 25

    bdt = train_model(X_train, y_train, X_valid, y_valid, config_dict, early_stopping_round)

    save_model(bdt, vars_list, loc.BDT)


def print_stats(df, modes):
    """Print the train/validation row count for each process in ``modes``."""
    print("__________________________________________________________")
    print("Input number of events:")
    for cur_mode in modes:
        print(f"Number of training {cur_mode}: {int(len(df[(df['sample'] == cur_mode) & (df['valid'] == False)]))}")
        print(f"Number of validation {cur_mode}: {int(len(df[(df['sample'] == cur_mode) & (df['valid'] == True)]))}")
    print("__________________________________________________________")


def split_data(df, vars_list):
    """Split ``df`` by the ``valid`` flag into ``(X_train, y_train, X_valid, y_valid)`` arrays.

    Features are the ``vars_list`` columns; the target is the binary ``isSignal``
    column. All four are returned as numpy arrays.
    """
    X_train = df.loc[df['valid'] == False, vars_list].to_numpy()
    y_train = df.loc[df['valid'] == False, ['isSignal']].to_numpy()
    X_valid = df.loc[df['valid'] == True, vars_list].to_numpy()
    y_valid = df.loc[df['valid'] == True, ['isSignal']].to_numpy()

    return X_train, y_train, X_valid, y_valid


def get_config_dict():
    """Return the XGBoost hyper-parameter dict for the binary classifier."""
    return {
        "n_estimators": 350,
        "learning_rate": 0.20,
        "max_depth": 3,
        'subsample': 0.5,
        'gamma': 3,
        'min_child_weight': 10,
        'max_delta_step': 0,
        'colsample_bytree': 0.5,
    }


def train_model(X_train, y_train, X_valid, y_valid, config_dict, early_stopping_round):
    """Fit and return an ``XGBClassifier`` with early stopping.

    Trains on ``(X_train, y_train)``, monitoring error/logloss/AUC on both the
    training and validation sets, and stops after ``early_stopping_round`` rounds
    without validation improvement.
    """
    bdt = xgb.XGBClassifier(**config_dict)

    eval_set = [(X_train, y_train), (X_valid, y_valid)]

    print("Training model")
    bdt.fit(X_train, y_train, eval_metric=["error", "logloss", "auc"], eval_set=eval_set,
            early_stopping_rounds=early_stopping_round, verbose=True)

    return bdt


def save_model(bdt, vars_list, output_path):
    """Persist the trained BDT under ``output_path`` in TMVA-ROOT and joblib formats.

    Writes ``xgb_bdt.root`` (via ``TMVA.Experimental.SaveXGBoost`` for RDataFrame
    inference, sized to ``len(vars_list)`` inputs) and ``xgb_bdt.joblib`` (for
    Python-side evaluation). Creates ``output_path`` if it does not exist.
    """
    ut.create_dir(output_path)
    print("--->Writing xgboost model:")
    print(f"------>Saving {output_path}/xgb_bdt.root")
    ROOT.TMVA.Experimental.SaveXGBoost(bdt, "Z_Recoil_BDT", f"{output_path}/xgb_bdt.root", num_inputs=len(vars_list))

    print(f"------>Saving {output_path}/xgb_bdt.joblib")
    joblib.dump(bdt, f"{output_path}/xgb_bdt.joblib")

if __name__ == "__main__":
    run()   


