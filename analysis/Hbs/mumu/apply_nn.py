import os
import sys
import glob
import argparse

import numpy as np
import uproot

from userConfig import loc
from train_nn import NN_DIR, NUM_CLASSES, load_model, preprocess, predict_proba

# Attach the NN scores to the stage-1 ntuples: NN replacement of step 6 of the
# README (stage1_include_bdt_batch_samples.py / _outside_data.py).
#
# Reads   <input>/<process>/chunk*.root   (stage-1 ntuples, steps 1-2)
# Writes  <output>/<process>/chunk*.root  with the same flat branches plus
#   BDTscore_class0..7 - NN class probabilities
#   norm_prob0..5      - P(rare_i) / (P(rare_i) + P(SM Higgs) + P(SM bkg))
# The branch names are those of the BDT chain on purpose, so that the final
# selection, plotting and Combine steps run unchanged on these files.
#
# The eventsProcessed counter used by "fccanalysis final" for the normalisation
# is copied over (with PyROOT: uproot cannot write TParameter objects).

INPUT_DIR = loc.TRAIN
OUTPUT_DIR = loc.EOS + '/NN_analysis_samples'

# counters written by fccanalysis next to the events tree
META = ["eventsProcessed", "eventsSelected", "eventsInput"]

STEP_SIZE = 500000  # events read / evaluated / written at a time


def run(input_dir, output_dir, processes):

    model, prep = load_model(NN_DIR)
    vars_list = prep["vars"]
    print("NN INPUT VARS")
    print(vars_list)

    if not processes:
        processes = sorted(os.path.basename(d) for d in glob.glob(f"{input_dir}/*") if glob.glob(f"{d}/*.root"))
    if not processes:
        sys.exit(f"ERROR: no <process>/*.root files found in {input_dir}")

    for process in processes:
        files = sorted(glob.glob(f"{input_dir}/{process}/*.root"))
        if not files:
            sys.exit(f"ERROR: no ROOT files found for process '{process}' in {input_dir}")

        n_events = 0
        n_processed = 0
        for f in files:
            fout = f"{output_dir}/{process}/{os.path.basename(f)}"
            n, meta = apply_to_file(f, fout, model, prep)
            n_events += n
            n_processed += meta.get("eventsProcessed", 0)
        print(f"--->{process}: {len(files)} files, {n_events} events in tree, {n_processed} events processed")

    print(f"Output written to {output_dir}")


def flat_branches(tree):
    # Only flat (one number per event) branches are copied. The per-jet vector
    # branches of the flavour tagger are dropped: the downstream steps only use
    # the jet1_*/jet2_* scalars.
    keep, dropped = {}, []
    for name, branch in tree.items(recursive=False):
        interp = branch.interpretation
        if isinstance(interp, uproot.AsDtype) and interp.to_dtype.shape == ():
            keep[name] = interp.to_dtype
        else:
            dropped.append(name)
    return keep, dropped


def score_branches():
    names = {f"BDTscore_class{i}": np.dtype("float32") for i in range(NUM_CLASSES)}
    names.update({f"norm_prob{i}": np.dtype("float64") for i in range(6)})
    return names


def compute_scores(arrays, model, prep):
    X = np.column_stack([arrays[v] for v in prep["vars"]]).astype(np.float32)
    proba = predict_proba(model, preprocess(X, prep))

    scores = {f"BDTscore_class{i}": proba[:, i].astype(np.float32) for i in range(NUM_CLASSES)}
    # Same quantity as in stage1_include_bdt_*.py, P_i / (1 - sum of the other
    # rare classes), written as P_i / (P_i + P_6 + P_7). The two are identical
    # since the probabilities sum to 1, but this form has no cancellation when
    # a softmax output saturates at 1. Set to 0 where the denominator vanishes.
    p = proba.astype(np.float64)
    for i in range(6):
        den = p[:, i] + p[:, 6] + p[:, 7]
        scores[f"norm_prob{i}"] = np.divide(p[:, i], den, out=np.zeros_like(den), where=den > 0)
    return scores


def apply_to_file(fin, fout, model, prep):
    os.makedirs(os.path.dirname(fout), exist_ok=True)
    # written under a name that "fccanalysis final" does not pick up
    # (it globs chunk*.root) and renamed once complete
    ftmp = f"{os.path.dirname(fout)}/tmp_{os.path.basename(fout)}"

    n_bad = 0
    with uproot.open(fin) as infile:
        meta = read_meta(infile)
        if "eventsProcessed" not in meta:
            sys.exit(f"ERROR: no eventsProcessed in {fin}, cannot normalise this sample")
        if "events" not in infile:
            sys.exit(f"ERROR: no events tree in {fin}")
        tree = infile["events"]

        new = score_branches()
        keep, _ = flat_branches(tree)
        keep = {k: v for k, v in keep.items() if k not in new}
        missing = [v for v in prep["vars"] if v not in keep]
        if missing:
            sys.exit(f"ERROR: NN input variables missing in {fin}: {missing}")

        with uproot.recreate(ftmp) as outfile:
            outfile.mktree("events", {**keep, **new})
            for arrays in tree.iterate(list(keep), step_size=STEP_SIZE, library="np"):
                scores = compute_scores(arrays, model, prep)
                n_bad += int(np.sum(~np.isfinite(scores["BDTscore_class0"])))
                outfile["events"].extend({**arrays, **scores})
        n_in = tree.num_entries

    write_meta(ftmp, meta)
    check_output(ftmp, n_in, meta)
    os.replace(ftmp, fout)

    msg = f"------>{fout}: {n_in} events"
    if n_bad:
        msg += f", WARNING: {n_bad} events with non-finite NN score (non-finite input variable), norm_prob set to 0"
    print(msg)
    return n_in, meta


def read_meta(infile):
    return {k: int(infile[k].value) for k in META if k in infile}


def write_meta(filename, meta):
    import ROOT
    outfile = ROOT.TFile.Open(filename, "UPDATE")
    if not outfile or outfile.IsZombie():
        sys.exit(f"ERROR: cannot update {filename}")
    for name, value in meta.items():
        ROOT.TParameter(int)(name, value).Write()
    outfile.Close()


def check_output(filename, n_in, meta):
    with uproot.open(filename) as f:
        n_out = f["events"].num_entries
        n_processed = int(f["eventsProcessed"].value)
    if n_out != n_in or n_processed != meta["eventsProcessed"]:
        sys.exit(f"ERROR: {filename} is inconsistent with its input "
                 f"(events {n_out} vs {n_in}, eventsProcessed {n_processed} vs {meta['eventsProcessed']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Attach the NN scores to the stage-1 ntuples')
    parser.add_argument("--input", dest="input_dir", default=INPUT_DIR, help="Directory with the stage-1 ntuples (<process>/chunk*.root)")
    parser.add_argument("--output", dest="output_dir", default=OUTPUT_DIR, help="Directory for the ntuples with NN scores")
    parser.add_argument("--processes", nargs="*", default=[], help="Processes to run on (default: all in the input directory)")
    args = vars(parser.parse_args())
    run(**args)
