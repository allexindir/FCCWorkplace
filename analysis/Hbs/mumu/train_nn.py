import os
import json
import copy

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rc
import joblib

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import log_loss, accuracy_score, confusion_matrix, ConfusionMatrixDisplay

from userConfig import loc, train_vars

NN_DIR = loc.EOS + '/NN'

NUM_CLASSES = 8
CLASS_NAMES = ["Hbs", "Huu", "Hdd", "Hcu", "Hsd", "Hbd", "SM_Higgs", "SM_bkg"]
LOG_VARS = ["d12", "d23", "d34", "d45"]

def run():
    vars_list = train_vars
    print("TRAINING VARS")
    print(vars_list)

    path = f"{loc.PKL}"
    df = pd.read_pickle(f"{path}/preprocessed.pkl")

    print("label counts:")
    print(df['label'].value_counts().sort_index())

    X_train, y_train, X_valid, y_valid = split_data(df, vars_list)
    X_train, y_train = drop_non_finite(X_train, y_train, "training")
    X_valid, y_valid = drop_non_finite(X_valid, y_valid, "validation")

    prep = get_preprocessing(X_train, vars_list)
    X_train = preprocess(X_train, prep)
    X_valid = preprocess(X_valid, prep)

    config = get_config_dict()

    model = build_model(config)

    history = train_model(model, X_train, y_train, X_valid, y_valid, config)
    save_model(model, prep, NN_DIR)
    plot_history(history, NN_DIR)
    plot_confusion_matrix(model, X_valid, y_valid, NN_DIR)

def split_data(df, vars_list):
    X_train = df.loc[df['valid'] == False, vars_list].to_numpy(dtype=np.float32)
    y_train = df.loc[df["valid"] == False, "label"].to_numpy().astype(int)

    X_valid = df.loc[df["valid"] == True, vars_list].to_numpy(dtype=np.float32)
    y_valid = df.loc[df["valid"] == True, "label"].to_numpy().astype(int)

    return X_train, y_train, X_valid, y_valid

def drop_non_finite(X, y, name):
    good = np.isfinite(X).all(axis=1)
    if not good.all():
        print(f'WARNING: dropping events with non-finite inputs')
    return X[good], y[good]

def get_config_dict():
    return {
        "hidden_layers": [128, 128, 128, 64],
        "activation": "relu",
        "alpha": 1e-4,
        "lr": 1e-3,
        "batch_size": 512,
        "epochs": 100,
        "early_stopping_round": 10,
        "seed": 7,
    }

def apply_log(X, log_mask):
    X = np.array(X, dtype=np.float32)
    log_mask = np.asarray(log_mask)
    if log_mask.dtype != bool or log_mask.shape != (X.shape[1],):
        raise ValueError(f'log mask must be one t/f per input var')
    X[:, log_mask] = np.log1p(np.maximum(X[:, log_mask], 0.0))
    return X

def get_preprocessing(X_train, vars_list):
    log_mask = np.array([v in LOG_VARS for v in vars_list])
    X = apply_log(X_train, log_mask)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0
    return {'vars': list(vars_list), 'log':log_mask, 'mean':mean, 'std':std}

def preprocess(X, prep):
    return (apply_log(X, prep['log']) - prep['mean']) / prep['std'] 

def build_model(config):
   return MLPClassifier(
           hidden_layer_sizes = tuple(config["hidden_layers"]),
           activation = config['activation'],
           solver = 'adam',
           alpha = config['alpha'],
           learning_rate_init = config['lr'],
           batch_size = config['batch_size'],
           shuffle = True,
           random_state = config['seed'],
    )

def predict_proba(model, X):
    proba = np.full((len(X), NUM_CLASSES), np.nan, dtype=np.float32)
    good = np.flatnonzero(np.isfinite(X).all(axis=1))
    for idx in np.array_split(good, max(1, len(good) // 100000)):
        if len(idx):
            proba[idx] = model.predict_proba(X[idx])
    return proba

def train_model(model, X_train, y_train, X_valid, y_valid, config):
    classes = np.arange(NUM_CLASSES)
    patience = config["early_stopping_round"]
    history = {"loss": [], "val_loss": [], "accuracy": [], "val_accuracy": []}
    best_loss, best_epoch, best_weights = np.inf, 0, None

    print("Training multiclass model")
    for epoch in range(1, config["epochs"] + 1):
        model.partial_fit(X_train, y_train, classes=classes)

        for name, X, y in [("", X_train, y_train), ("val_", X_valid, y_valid)]:
            proba = predict_proba(model, X)
            history[f"{name}loss"].append(log_loss(y, proba, labels=classes))
            history[f"{name}accuracy"].append(accuracy_score(y, np.argmax(proba, axis=1)))
        print(f"Epoch {epoch:3d}: loss {history['loss'][-1]:.4f}, val_loss {history['val_loss'][-1]:.4f}, "
              f"accuracy {history['accuracy'][-1]:.4f}, val_accuracy {history['val_accuracy'][-1]:.4f}")

        if history["val_loss"][-1] < best_loss:
            best_loss, best_epoch = history["val_loss"][-1], epoch
            best_weights = copy.deepcopy((model.coefs_, model.intercepts_))
        elif epoch - best_epoch >= patience:
            print(f"Early stopping: no improvement of val_loss for {patience} epochs")
            break

    print(f"Restoring model weights from the best epoch: {best_epoch}")
    model.coefs_, model.intercepts_ = best_weights

    return history

def save_model(model, prep, out_path):
    os.makedirs(out_path, exist_ok=True)
    print("--->Writing NN model:")

    print(f"------>Saving {out_path}/nn_model.joblib")
    joblib.dump(model, f"{out_path}/nn_model.joblib")

    print(f"------>Saving {out_path}/nn_preprocessing.json")
    with open(f"{out_path}/nn_preprocessing.json", "w") as f:
        json.dump({
            "vars": prep["vars"],
            "log": [bool(b) for b in prep["log"]],
            "mean": [float(x) for x in prep["mean"]],
            "std": [float(x) for x in prep["std"]],
        }, f, indent=2)

def load_model(out_path):
    print(f'loading NN model {out_path}/nn_model.joblib')
    model = joblib.load(f'{out_path}/nn_model.joblib')
    with open(f'{out_path}/nn_preprocessing.json') as f:
        prep = json.load(f)

    prep['log'] = np.array(prep['log'], dtype=bool)
    prep['mean'] = np.array(prep['mean'], dtype=np.float32)
    prep['std'] = np.array(prep['std'], dtype=np.float32)
    return model, prep 

def plot_history(history, output_path):
    for key, ylabel in [("loss", "Log Loss"), ("accuracy", "Accuracy")]:
        print(f"------>Plotting {key}")
        fig, ax = plt.subplots()
        ax.plot(range(1, len(history[key]) + 1), history[key], label="Training")
        ax.plot(range(1, len(history[key]) + 1), history[f"val_{key}"], label="Validation")
        ax.legend()
        plt.xlabel("Epoch")
        plt.ylabel(ylabel)
        ax.set_title('FCC-ee Simulation', fontsize=16, loc='left')
        ax.set_title(r"$Z(\mu^+\mu^-)H$", fontsize=16, loc='right')
        plt.savefig(f"{output_path}/nn_{key}.png")
        plt.savefig(f"{output_path}/nn_{key}.pdf")
        plt.close()

def plot_confusion_matrix(model, X_valid, y_valid, out_path):
    print("------>Plotting confusion matrix")
    y_pred = np.argmax(predict_proba(model, X_valid), axis=1)
    print(f"Validation accuracy: {accuracy_score(y_valid, y_pred):.4f}")

    cm = confusion_matrix(y_valid, y_pred, labels=list(range(NUM_CLASSES)), normalize="true") 

    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASS_NAMES)
    disp.plot(ax=ax, cmap="Blues", values_format=".3f", colorbar=True)
    plt.xticks(rotation=45, ha="right")
    ax.set_title('FCC-ee simulation', fontsize=16, loc='left', fontweight='bold')
    ax.set_title(r"$Z(\mu^+\mu^-)H$", fontsize=16, loc="right")
    plt.tight_layout()
    plt.savefig(f"{out_path}/nn_confusion_matrix.png")
    plt.savefig(f"{out_path}/nn_confusion_matrix.pdf")
    plt.close()

if __name__ == '__main__':
    run()

