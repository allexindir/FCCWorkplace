import os
import sys
import json
import argparse

import uproot

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from repo_paths import analysis_path
from merge_fv_inputs import ENERGY, read_samples

# Write the cross-section dictionary fcc-fv-analysis reads through
#   analysis.process_dictionary: {json: <this file>}
# and print the BR references for its pilot (scan:) and fitter (fit:) configs.
#
# The cross sections are the crossSection parameters "fccanalysis final"
# stored in Histo_Files_NN. procDictAdd overrides FCCDicts there, so these are
# the values our chain normalised with, and both chains get the same yields.
#
# BR_ref = sigma(sample) / sigma(ee->mumuH) is the branching fraction a sample
# stands for at r = 1, the same conversion as the datacard headers written by
# combine/make_datacards.py. fcc-fv-analysis uses it to scale the rare modes to
# the trial BR in the boundary scan and to turn r into a BR in the final table,
# so the pilot and fitter configs must carry the same values.
#
# Run after `source setup_hbs.sh` (needs uproot).

HISTO_DIR = analysis_path("Histo_Files_NN")
OUTPUT = os.path.join(HERE, "procdict_mumu.json")

SELECTION = "sel_Baseline_no_costhetamiss"
XSEC_MUMUH = 0.0067643  # pb, wzp6_ee_mumuH_ecm240, as in combine/make_datacards.py

# fcc-fv-analysis class -> sample standing for it
RARE = {
    "Hbs": "wzp6_ee_mumuH_Hbs",
    "Huu": "wzp6_ee_mumuH_Huu",
    "Hdd": "wzp6_ee_mumuH_Hdd",
    "Hcu": "wzp6_ee_mumuH_Hcu",
    "Hsd": "wzp6_ee_mumuH_Hsd",
    "Hbd": "wzp6_ee_mumuH_Hbd",
}


def cross_section(filename):
    with uproot.open(filename) as f:
        if "crossSection" not in f:
            sys.exit(f"ERROR: no crossSection in {filename}")
        return float(f["crossSection"].value)


def run(histo_dir, output):
    procdict = {}
    for ours, theirs in read_samples():
        if not theirs:
            continue
        filename = os.path.join(histo_dir, f"{ours}_{SELECTION}_histo.root")
        if not os.path.isfile(filename):
            sys.exit(f"ERROR: {filename} not found, run step 7 with HBS_CLASSIFIER=NN first")
        xsec = cross_section(filename)
        if not xsec > 0:
            sys.exit(f"ERROR: invalid crossSection {xsec} in {filename}")
        procdict[f"{theirs}_ecm{ENERGY}"] = {"crossSection": xsec}
        print(f"--->{theirs}: {xsec:.6g} pb")

    missing = [sample for sample in RARE.values() if f"{sample}_ecm{ENERGY}" not in procdict]
    if missing:
        sys.exit(f"ERROR: rare-mode samples missing from fv_samples.txt: {missing}")

    with open(output, "w") as f:
        json.dump(procdict, f, indent=2)
        f.write("\n")
    print(f"Cross sections written to {output}")

    br_ref = {name: procdict[f"{sample}_ecm{ENERGY}"]["crossSection"] / XSEC_MUMUH for name, sample in RARE.items()}
    print("\nBR references, for scan: in the pilot config and fit: in the fitter config:")
    print("  branching_ratio_reference: {" + ", ".join(f"{name}: {value:.10g}" for name, value in br_ref.items()) + "}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write the fcc-fv-analysis cross-section dictionary and BR references')
    parser.add_argument("--histo-dir", dest="histo_dir", default=HISTO_DIR, help="Step-7 histogram files of the NN chain")
    parser.add_argument("--output", default=OUTPUT, help="JSON file to write (point process_dictionary.json at it)")
    args = vars(parser.parse_args())
    run(**args)
