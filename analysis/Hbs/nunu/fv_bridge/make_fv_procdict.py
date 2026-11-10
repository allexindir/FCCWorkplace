import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from merge_fv_inputs import ENERGY, read_samples

# Write the cross-section dictionary fcc-fv-analysis reads through
#   analysis.process_dictionary: {json: <this file>}
# and print the BR references for its pilot (scan:) and fitter (fit:) configs.
#
# The mumu version reads the cross sections back from the step-7 histograms.
# The nunu chain has no step 7 yet, so here they come from FCCDicts for the
# official samples and from CUSTOM_XSEC for our own FCNC samples (CUSTOM_XSEC
# wins, as procDictAdd does in "fccanalysis final"). The custom values are
# placeholders: any value gives the same BR limits, as long as the BR_ref
# printed below goes into both configs.
#
# BR_ref = sigma(sample) / sigma(ee->nunuH) is the branching fraction a sample
# stands for at r = 1. fcc-fv-analysis uses it to scale the rare modes to the
# trial BR in the boundary scan and to turn r into a BR in the final table.
# It assumes the custom samples were generated with the same neutrino flavours
# (and WW fusion) as wzp6_ee_nunuH_ecm240.
#
# Run after `source setup_hbs.sh` on SDCC (needs /cvmfs, and uproot through
# merge_fv_inputs).

PROCDICT = "/cvmfs/fcc.cern.ch/FCCDicts/FCCee_procDict_winter2023_IDEA.json"
OUTPUT = os.path.join(HERE, "procdict_nunu.json")

XSEC_REFERENCE = "wzp6_ee_nunuH_ecm240"  # sigma(ee->nunuH), BR = r * sigma_sample / sigma(ee->nunuH)

# pb, placeholders for the samples that are not in FCCDicts
CUSTOM_XSEC = {
    "wzp6_ee_nunuH_Hbs_W4p1MeV_ecm240": 0.01,
    "wzp6_ee_nunuH_Hbd_W4p1MeV_ecm240": 0.01,
    "wzp6_ee_nunuH_Hcu_W4p1MeV_ecm240": 0.01,
    "wzp6_ee_nunuH_Hsd_W4p1MeV_ecm240": 0.01,
    "wzp6_ee_nunuH_Huu_ecm240":         0.01,
    "wzp6_ee_nunuH_Hdd_ecm240":         0.01,
}

# fcc-fv-analysis class -> sample standing for it
RARE = {
    "Hbs": "wzp6_ee_nunuH_Hbs",
    "Huu": "wzp6_ee_nunuH_Huu",
    "Hdd": "wzp6_ee_nunuH_Hdd",
    "Hcu": "wzp6_ee_nunuH_Hcu",
    "Hsd": "wzp6_ee_nunuH_Hsd",
    "Hbd": "wzp6_ee_nunuH_Hbd",
}


def cross_section(process, fccdicts):
    if process in CUSTOM_XSEC:
        return CUSTOM_XSEC[process]
    if process not in fccdicts:
        sys.exit(f"ERROR: {process} is neither in CUSTOM_XSEC nor in FCCDicts")
    return float(fccdicts[process]["crossSection"])


def run(procdict, output):
    with open(procdict) as f:
        fccdicts = json.load(f)

    out = {}
    for ours, theirs in read_samples():
        if not theirs:
            continue
        xsec = cross_section(ours, fccdicts)
        if not xsec > 0:
            sys.exit(f"ERROR: invalid crossSection {xsec} for {ours}")
        out[f"{theirs}_ecm{ENERGY}"] = {"crossSection": xsec}
        source = "CUSTOM_XSEC" if ours in CUSTOM_XSEC else "FCCDicts"
        print(f"--->{theirs}: {xsec:.6g} pb ({source})")

    missing = [sample for sample in RARE.values() if f"{sample}_ecm{ENERGY}" not in out]
    if missing:
        sys.exit(f"ERROR: rare-mode samples missing from fv_samples.txt: {missing}")

    with open(output, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"Cross sections written to {output}")

    xsec_ref = cross_section(XSEC_REFERENCE, fccdicts)
    print(f"\nsigma(ee->nunuH) = {xsec_ref:.6g} pb ({XSEC_REFERENCE})")
    br_ref = {name: out[f"{sample}_ecm{ENERGY}"]["crossSection"] / xsec_ref for name, sample in RARE.items()}
    print("BR references, for scan: in the pilot config and fit: in the fitter config:")
    print("  branching_ratio_reference:")
    for name, value in br_ref.items():
        print(f"    {name}: {value:.10g}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write the fcc-fv-analysis cross-section dictionary and BR references')
    parser.add_argument("--procdict", default=PROCDICT, help="FCCDicts process dictionary for the official samples")
    parser.add_argument("--output", default=OUTPUT, help="JSON file to write (point process_dictionary.json at it)")
    args = vars(parser.parse_args())
    run(**args)