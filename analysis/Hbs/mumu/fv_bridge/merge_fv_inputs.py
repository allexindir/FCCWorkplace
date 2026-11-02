import os
import sys
import glob
import argparse
import subprocess

import uproot

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from repo_paths import analysis_path

# Merge the NN_analysis_samples chunks into the one-file-per-sample layout read
# by the fcc-fv-analysis categorizer, so our NN scores can go through their
# boundary scan and recoil-mass fit.
#
# Reads   <input>/<our process>/chunk*.root          (apply_nn.py output)
# Writes  <output>/<their sample>_ecm240_finalsel.root
# with the names from fv_samples.txt.
#
# hadd sums the eventsProcessed counters, which fcc-fv-analysis uses as the
# number of generated events (their files have no sumOfWeights, so it falls
# back to eventsProcessed). The merged value is checked against the sum over
# the chunks.
#
# Run after `source setup_hbs.sh` (needs hadd and uproot).

SAMPLES_FILE = os.path.join(HERE, "fv_samples.txt")
INPUT_DIR = analysis_path("NN_analysis_samples")
OUTPUT_DIR = analysis_path("fv_inputs_mumu")

ENERGY = 240


def read_samples(path=SAMPLES_FILE):
    # [(our process, their sample)], their sample is None for "-" lines
    rows = []
    with open(path) as f:
        for line in f:
            fields = line.split("#", 1)[0].split()
            if not fields:
                continue
            if len(fields) != 2:
                sys.exit(f"ERROR: expected '<our process> <their sample>' in {path}: {line.rstrip()}")
            ours, theirs = fields
            rows.append((ours, None if theirs == "-" else theirs))

    ours_names = [ours for ours, _ in rows]
    theirs_names = [theirs for _, theirs in rows if theirs]
    for names in (ours_names, theirs_names):
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            sys.exit(f"ERROR: listed more than once in {path}: {duplicates}")
    return rows


def output_name(sample):
    return f"{sample}_ecm{ENERGY}_finalsel.root"


def events_processed(filename):
    with uproot.open(filename) as f:
        if "eventsProcessed" not in f:
            sys.exit(f"ERROR: no eventsProcessed in {filename}, cannot normalise this sample")
        return int(f["eventsProcessed"].value)


def run(input_dir, output_dir, dry_run):
    rows = read_samples()
    mapped = {ours: theirs for ours, theirs in rows if theirs}
    skipped = {ours for ours, theirs in rows if not theirs}

    # Every process apply_nn.py scored must be listed, either mapped or "-",
    # so nothing is silently added to or dropped from the fit.
    present = sorted(d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d)))
    unlisted = [d for d in present if d not in mapped and d not in skipped]
    if unlisted:
        sys.exit(f"ERROR: processes in {input_dir} missing from {SAMPLES_FILE}: {unlisted}")
    missing = [ours for ours in mapped if ours not in present]
    if missing:
        sys.exit(f"ERROR: processes listed in {SAMPLES_FILE} but not found in {input_dir}: {missing}")

    # fcc-fv-analysis looks for ../hists/*_selNone_histo.root when the input
    # directory is called "trees" (categorizer/physics.py)
    if os.path.basename(os.path.normpath(output_dir)) == "trees":
        sys.exit("ERROR: do not name the output directory 'trees'")

    for ours in sorted(skipped & set(present)):
        print(f"--->{ours}: skipped")

    if not dry_run:
        os.makedirs(output_dir, exist_ok=True)

    for ours, theirs in mapped.items():
        chunks = sorted(glob.glob(f"{input_dir}/{ours}/chunk*.root"))
        if not chunks:
            sys.exit(f"ERROR: no chunk*.root files in {input_dir}/{ours}")
        fout = os.path.join(output_dir, output_name(theirs))

        if dry_run:
            print(f"--->{ours} -> {fout} ({len(chunks)} chunks)")
            continue

        subprocess.run(["hadd", "-f", fout] + chunks, check=True, stdout=subprocess.DEVNULL)

        n_expected = sum(events_processed(c) for c in chunks)
        n_processed = events_processed(fout)
        if n_processed != n_expected:
            sys.exit(f"ERROR: {fout} has eventsProcessed {n_processed}, the chunks sum to {n_expected}")
        with uproot.open(fout) as f:
            n_events = f["events"].num_entries
        print(f"--->{theirs}: {len(chunks)} chunks, {n_events} events in tree, {n_processed} events processed")

    if not dry_run:
        print(f"Output written to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge NN_analysis_samples into the fcc-fv-analysis input layout')
    parser.add_argument("--input", dest="input_dir", default=INPUT_DIR, help="Directory with the NN-scored ntuples (<process>/chunk*.root)")
    parser.add_argument("--output", dest="output_dir", default=OUTPUT_DIR, help="Directory for <sample>_ecm240_finalsel.root")
    parser.add_argument("--dry-run", action="store_true", help="Check the sample list and print the merges without running hadd")
    args = vars(parser.parse_args())
    run(**args)
