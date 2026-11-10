import numpy as np
import os
import sys

# Locate the FCCWorkplace checkout so the paths below follow the repo, not a
# particular user area (override with FCCWORKPLACE_ROOT).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repo_paths import analysis_path


#python examples/FCCee/higgs/mH-recoil/mumu/finalSel.py
#Input directory where the files produced at the pre-selection level are
inputDir = analysis_path("NN_analysis_samples")

#Output directory for the plotting script
outputDir = analysis_path("Histo_Files_NN")

###Link to the dictonary that contains all the cross section informations etc...
procDict = "FCCee_procDict_winter2023_IDEA.json"
# Our own FCNC samples are not in FCCDicts. The cross sections are the same
# placeholders as CUSTOM_XSEC in fv_bridge/make_fv_procdict.py (keep the two in
# sync): BR = r * sigma_placeholder / sigma(ee->nunuH). The histograms are
# normalised with the eventsProcessed counters of the input files, so only the
# cross section is needed here.
procDictAdd = {
    "wzp6_ee_nunuH_Hbs_W4p1MeV_ecm240": {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
    "wzp6_ee_nunuH_Hbd_W4p1MeV_ecm240": {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
    "wzp6_ee_nunuH_Hcu_W4p1MeV_ecm240": {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
    "wzp6_ee_nunuH_Hsd_W4p1MeV_ecm240": {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
    "wzp6_ee_nunuH_Huu_ecm240":         {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
    "wzp6_ee_nunuH_Hdd_ecm240":         {"crossSection": 0.01, "kfactor": 1.0, "matchingEfficiency": 1.0},
}


###Process list that should match the produced files.
processList = [
    # Off-Diagonal Higgs Decays (FCNC Signals)
    "wzp6_ee_nunuH_Hbs_W4p1MeV_ecm240",
    "wzp6_ee_nunuH_Hbd_W4p1MeV_ecm240",
    "wzp6_ee_nunuH_Hcu_W4p1MeV_ecm240",
    "wzp6_ee_nunuH_Hsd_W4p1MeV_ecm240",

    # Higgs Decays (Bosons / Leptons)
    "wzp6_ee_nunuH_HWW_ecm240",
    "wzp6_ee_nunuH_HZZ_noInv_ecm240",
    "wzp6_ee_nunuH_Htautau_ecm240",
    "wzp6_ee_nunuH_HZa_ecm240",

    # Diagonal Higgs Decays (Quarks & Gluons)
    "wzp6_ee_nunuH_Hbb_ecm240",
    "wzp6_ee_nunuH_Hss_ecm240",
    "wzp6_ee_nunuH_Hcc_ecm240",
    "wzp6_ee_nunuH_Hgg_ecm240",
    "wzp6_ee_nunuH_Huu_ecm240",
    "wzp6_ee_nunuH_Hdd_ecm240",

    # Standard Model Backgrounds
    "wzp6_ee_nunuH_ecm240",  # inclusive, overlaps with the exclusive decays above
    "p8_ee_ZZ_ecm240",
    "p8_ee_WW_ecm240",
    "p8_ee_Zqq_ecm240",
    "wzp6_ee_nuenueZ_ecm240",
]

#Number of CPUs to use
nCPUS = 2
#produces ROOT TTrees, default is False
doTree = False

###Dictionary of the list of cuts. The key is the name of the selection that will be added to the output file
# Stage 1 already requires no isolated e/mu with p > 20 GeV, missing_m > 40 GeV
# and two exclusive jets. The baseline is the nunu analogue of the mumu one:
# the missing mass plays the role of m_ll (Z -> nunu), the dijet mass that of
# the recoil mass, and p_jj (= p_miss) that of p_ll. Provisional: it keeps ~89%
# of H->bs and ~7% of WW/ZZ, ~2% of Zqq/nuenueZ (stage-1 ntuples, unweighted).
cutList = {
            #Without Cuts
            "No_Cuts":"1",
            "APC_Cuts":"higgs_m < 140 && higgs_m > 120 && missing_m > 81 && missing_m < 101 && event_d23 > 0 && event_d34 > 0"
            }

###Dictionary for the ouput variable/hitograms. The key is the name of the variable in the output files. "name" is the name of the variable in the input file, "title" is the x-axis label of the histogram, "bin" the number of bins of the histogram, "xmin" the minimum x-axis value and "xmax" the maximum x-axis value.
histoList = {
    # 2D plot histo:
    "met_p_vs_met_theta": {"cols": ["met_p", "met_theta"], "bins": [(60, 0, 120), (50, 0, np.pi)]},

    # ── Missing Momentum (Z -> nunu) ──────────────────────────────────────────
    # p_miss is minus the sum of the reconstructed particles, which are all
    # clustered into the two jets: met_p == higgs_p and met_pt == higgs_pt.
    "missing_m": {"name": "missing_m", "title": "m_{miss} [GeV]", "bin": 100, "xmin": 40, "xmax": 240},
    "met_p": {"name": "met_p", "title": "p_{miss} [GeV]", "bin": 60, "xmin": 0, "xmax": 120},
    "met_pt": {"name": "met_pt", "title": "p_{T,miss} [GeV]", "bin": 50, "xmin": 0, "xmax": 100},
    "met_theta": {"name": "met_theta", "title": "#theta_{miss}", "bin": 100, "xmin": 0, "xmax": np.pi},
    "met_phi": {"name": "met_phi", "title": "#phi_{miss}", "bin": 100, "xmin": -np.pi, "xmax": np.pi},
    "cosTheta_miss": {"name": "cosTheta_miss", "title": "cos#theta_{miss}", "bin": 100, "xmin": -1, "xmax": 1},

    # ── Higgs Candidate (dijet) ────────────────────────────────────────────────
    "higgs_m": {"name": "higgs_m", "title": "m_{jj} [GeV]", "bin": 100, "xmin": 0, "xmax": 200},
    "higgs_p": {"name": "higgs_p", "title": "p_{jj} [GeV]", "bin": 60, "xmin": 0, "xmax": 120},
    "higgs_pt": {"name": "higgs_pt", "title": "p_{T,jj} [GeV]", "bin": 50, "xmin": 0, "xmax": 100},
    "higgs_e": {"name": "higgs_e", "title": "E_{jj} [GeV]", "bin": 100, "xmin": 0, "xmax": 200},
    "higgs_theta": {"name": "higgs_theta", "title": "#theta_{jj}", "bin": 100, "xmin": 0, "xmax": np.pi},
    "jets_acolinearity": {"name": "jets_acolinearity", "title": "|#theta_{j1} + #theta_{j2} - #pi|", "bin": 100, "xmin": 0, "xmax": 3.2},
    "jets_acoplanarity": {"name": "jets_acoplanarity", "title": "#pi - |#Delta#phi_{jj}|", "bin": 100, "xmin": 0, "xmax": 3.2},

    # ── Jet Flavor Tagging Scores ──────────────────────────────────────────────
    # The tagger output saturates at exactly 1 (e.g. the tau score of ~6% of
    # the WW jets), which a [0, 1] axis puts in the overflow: the extra last bin
    # [1, 1.01] keeps those jets on the plots.
    "btag_max": {"name": "btag_max", "title": "max b-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "stag_other": {"name": "stag_other", "title": "other s-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_btag": {"name": "jet1_btag", "title": "Jet 1 b-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_btag": {"name": "jet2_btag", "title": "Jet 2 b-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_stag": {"name": "jet1_stag", "title": "Jet 1 s-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_stag": {"name": "jet2_stag", "title": "Jet 2 s-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_ctag": {"name": "jet1_ctag", "title": "Jet 1 c-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_ctag": {"name": "jet2_ctag", "title": "Jet 2 c-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_utag": {"name": "jet1_utag", "title": "Jet 1 u-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_utag": {"name": "jet2_utag", "title": "Jet 2 u-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_dtag": {"name": "jet1_dtag", "title": "Jet 1 d-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_dtag": {"name": "jet2_dtag", "title": "Jet 2 d-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_Gtag": {"name": "jet1_Gtag", "title": "Jet 1 gluon-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_Gtag": {"name": "jet2_Gtag", "title": "Jet 2 gluon-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet1_tautag": {"name": "jet1_tautag", "title": "Jet 1 tau-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},
    "jet2_tautag": {"name": "jet2_tautag", "title": "Jet 2 tau-tag score", "bin": 101, "xmin": 0, "xmax": 1.01},

    # ── Jet Kinematics and Merging Scales ──────────────────────────────────────
    "jet1_p": {"name": "jet1_p", "title": "p_{jet 1} [GeV]", "bin": 140, "xmin": 0, "xmax": 140},
    "jet2_p": {"name": "jet2_p", "title": "p_{jet 2} [GeV]", "bin": 100, "xmin": 0, "xmax": 100},
    "jet1_E": {"name": "jet1_E", "title": "E_{jet 1} [GeV]", "bin": 140, "xmin": 0, "xmax": 140},
    "jet2_E": {"name": "jet2_E", "title": "E_{jet 2} [GeV]", "bin": 100, "xmin": 0, "xmax": 100},
    "jet1_mass": {"name": "jet1_mass", "title": "m_{jet 1} [GeV]", "bin": 120, "xmin": 0, "xmax": 120},  # W-mass jets in hadronic WW
    "jet2_mass": {"name": "jet2_mass", "title": "m_{jet 2} [GeV]", "bin": 80, "xmin": 0, "xmax": 80},
    "jet1_theta": {"name": "jet1_theta", "title": "#theta_{jet 1}", "bin": 100, "xmin": 0, "xmax": np.pi},
    "jet2_theta": {"name": "jet2_theta", "title": "#theta_{jet 2}", "bin": 100, "xmin": 0, "xmax": np.pi},
    "jet1_phi": {"name": "jet1_phi", "title": "#phi_{jet 1}", "bin": 100, "xmin": 0, "xmax": 2 * np.pi},  # jet_phi is in [0, 2pi]
    "jet2_phi": {"name": "jet2_phi", "title": "#phi_{jet 2}", "bin": 100, "xmin": 0, "xmax": 2 * np.pi},
    "jet1_nconst": {"name": "jet1_nconst", "title": "Constituent multiplicity (Jet 1)", "bin": 80, "xmin": 0, "xmax": 80},
    "jet2_nconst": {"name": "jet2_nconst", "title": "Constituent multiplicity (Jet 2)", "bin": 80, "xmin": 0, "xmax": 80},
    "event_d12": {"name": "event_d12", "title": "d_{12} jet-merging scale [GeV^{2}]", "bin": 70, "xmin": 0, "xmax": 35000},
    "event_d23": {"name": "event_d23", "title": "d_{23} jet-merging scale [GeV^{2}]", "bin": 80, "xmin": 0, "xmax": 8000},
    "event_d34": {"name": "event_d34", "title": "d_{34} jet-merging scale [GeV^{2}]", "bin": 100, "xmin": 0, "xmax": 1500},
    "event_d45": {"name": "event_d45", "title": "d_{45} jet-merging scale [GeV^{2}]", "bin": 100, "xmin": 0, "xmax": 300},
}

# ── Multi-Class NN Output Scores ──────────────────────────────────────────────
# apply_nn.py keeps the BDT branch names: BDTscore_class<i> is the NN
# probability of class i (CLASS_NAMES in train_nn.py), and norm_prob<i> is
# P(i) / (P(i) + P(SM H) + P(SM bkg)) for the six rare classes.
nn_classes = ["H#rightarrowbs", "H#rightarrowuu", "H#rightarrowdd", "H#rightarrowcu",
              "H#rightarrowsd", "H#rightarrowbd", "SM H", "SM bkg"]
for i, cls in enumerate(nn_classes):
    histoList[f"BDTscore_class{i}"] = {"name": f"BDTscore_class{i}", "title": f"NN score P({cls})", "bin": 20, "xmin": 0.0, "xmax": 1.0}
for i, cls in enumerate(nn_classes[:6]):
    histoList[f"norm_prob{i}"] = {"name": f"norm_prob{i}", "title": f"P({cls}) / (P({cls}) + P(SM))", "bin": 20, "xmin": 0.0, "xmax": 1.0}
