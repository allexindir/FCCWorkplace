import uproot
import numpy as np
import matplotlib.pyplot as plt
import os
import glob 

outdir = "/eos/user/d/dduan/FCCee/Hbs/mumu/visualize_graphs/"

samples = {
    "H→bs (Signal)":        "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hbs_W4p1MeV_ecm240",
    "H→bd (Signal)":        "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hbd_W4p1MeV_ecm240",
    "H→cu (Signal)":        "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hcu_W4p1MeV_ecm240",
    "H→sd (Signal)":        "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hsd_W4p1MeV_ecm240",

    # Other Higgs Decays
    "H→WW":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_HWW_ecm240",
    "H→ZZ (noInv)":         "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_HZZ_noInv_ecm240",
    "H→ττ":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Htautau_ecm240",
    "H→Zγ":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_HZa_ecm240",

    # Diagonal Higgs Decay signals
    "H→bb":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hbb_ecm240",
    "H→ss":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hss_ecm240",
    "H→cc":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hcc_ecm240",
    "H→dd":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hdd_ecm240",
    "H→uu":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Huu_ecm240",
    "H→gg":                 "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hgg_ecm240",

    # Other backgrounds
    "ZH (inclusive)":       "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_ecm240",
    "ZZ":                   "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/p8_ee_ZZ_ecm240",
    "WW (inclusive)":       "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/p8_ee_WW_ecm240",
    "Z/γ→μμ":               "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumu_ecm240",
    "eγ→eZ→μμ":             "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_egamma_eZ_Zmumu_ecm240",
    "γe→eZ→μμ":             "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_gammae_eZ_Zmumu_ecm240",
    "γγ→μμ":                "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_gaga_mumu_60_ecm240",

    # Old backgrounds/signals
    #"WW→μμ":                "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/p8_ee_WW_mumu_ecm240",
    #"H→bb (Signal)":        "/eos/user/d/dduan/FCCee/Hbs/mumu/BDT_analysis_samples/wzp6_ee_mumuH_Hbb_MEdecay_ecm240",
}                  

colors = {
    # Off-Diagonal Higgs Decay signals
    "H→bs (Signal)":        "black",
    "H→bd (Signal)":        "tomato",
    "H→cu (Signal)":        "sandybrown",
    "H→sd (Signal)":        "gold",

    # Diagonal Higgs Decays
    "H→bb":                 "darkorange",
    "H→ss":                 "crimson",
    "H→cc":                 "mediumslateblue",
    "H→uu":                 "lightcoral",
    "H→dd":                 "indianred",
    "H→gg":                 "goldenrod",

    # Other Higgs Decays
    "H→WW":                 "firebrick",
    "H→ZZ (noInv)":         "mediumvioletred",
    "H→ττ":                 "deeppink",
    "H→Zγ":                 "orchid",

    # Non-Higgs Backgrounds (Distinct cool, deep, and neutral tones)
    "ZH (inclusive)":       "indigo",
    "ZZ":                   "forestgreen",
    "WW (inclusive)":       "darkcyan",
    "Z/γ→μμ":               "turquoise",
    "eγ→eZ→μμ":             "khaki",
    "γe→eZ→μμ":             "olive",
    "γγ→μμ":                "slategray",

    # Old Signal/Backgrounds
    #"WW→μμ":                "dodgerblue",
    #"H→bb (final_state)":   "darkorchid",
}

branches = [
    # MET
    "met_p", "met_pt", "met_theta", "met_phi",
    "met_px", "met_py", "met_pz",
    "higgs_met_m", "higgs_met_e",
    
    # Total E and mass
    "total_m", "total_e",
    
    # Z leptonic
    "zll_m", "zll_p", "zll_theta",
    "zll_recoil_m",
    
    # Z leptons
    "leading_zll_lepton_p",    "leading_zll_lepton_theta",
    "subleading_zll_lepton_p", "subleading_zll_lepton_theta",
    "zll_leptons_acolinearity", "zll_leptons_acoplanarity",
    
    # Higgs candidate (dijet)
    "higgs_m",
    
    # Jets
    "jet1_p", "jet1_theta", "jet1_phi", "jet1_mass",
    "jet2_p", "jet2_theta", "jet2_phi", "jet2_mass",
    "event_d12", "event_d23", "event_d34", "event_d45",
    "jet1_E", "jet2_E",
    "jet1_nconst", "jet2_nconst",
    # "jet1_charge", "jet2_charge",

    # Flavor tags
    "jet1_btag", "jet2_btag",
    "jet1_stag", "jet2_stag",
    "jet1_ctag", "jet2_ctag",
    "jet1_utag", "jet2_utag",
    "jet1_dtag", "jet2_dtag",
    "jet1_Gtag", "jet2_Gtag",
    "jet1_tautag", "jet2_tautag",
    "btag_max",  "stag_other",

    # Event level
    "cosTheta_miss",
    
    # Gen tag (used to define signal in training, not a BDT input)
    "is_Hbs",
    
    # Gen-quark kinematics
    "gen_b_p", "gen_b_theta", "gen_b_phi", "gen_b_pdg",
    "gen_s_p", "gen_s_theta", "gen_s_phi", "gen_s_pdg",

    # Non-normalized probability score
    "BDTscore_class0", 
    "BDTscore_class1", 
    "BDTscore_class2", 
    "BDTscore_class3",
    "BDTscore_class4", 
    "BDTscore_class5", 
    "BDTscore_class6", 
    "BDTscore_class7",

    # Normalized probability score
    "norm_prob0", 
    "norm_prob1", 
    "norm_prob2", 
    "norm_prob3", 
    "norm_prob4", 
    "norm_prob5",
]

#Load all files
data = {}
for name, dir_path in samples.items():
    # Construct a search pattern for any .root files inside the directory or its subdirectories
    search_pattern = os.path.join(dir_path, "**/*.root")
    file_list = glob.glob(search_pattern, recursive=True)
    
    if not file_list:
        print(f"Warning: No .root files found in {dir_path}")
        continue
        
    print(f"Loading {len(file_list)} files for {name}...")
    
    # Target the 'events' tree inside every file paths in our list
    tree_paths = [f"{f}:events" for f in file_list]
    
    # Concatenate all trees directly into a dictionary of numpy arrays
    data[name] = uproot.concatenate(tree_paths, expressions=branches, library="np")

labels = {
    # MET & Missing Kinematics
    "met_p": "p_{miss} [GeV]",
    "met_pt": "p_{T, miss} [GeV]",
    "met_theta": "#theta_{miss}",
    "met_phi": "#phi_{miss}",
    "met_px": "p_{x, miss} [GeV]",
    "met_py": "p_{y, miss} [GeV]",
    "met_pz": "p_{z, miss} [GeV]",
    "higgs_met_m": "m_{jj + MET} [GeV]",
    "higgs_met_e": "E_{jj + MET} [GeV]",
    "cosTheta_miss": "cos(#theta_{miss})",

    # Total E and Mass
    "total_m": "m_{tot} [GeV]",
    "total_e": "E_{tot} [GeV]",

    # Z Leptonic & Leptons
    "zll_m": "m_{ll} [GeV]",
    "zll_p": "p_{ll} [GeV]",
    "zll_theta": "#theta_{ll}",
    "zll_recoil_m": "m_{recoil} [GeV]",
    "leading_zll_lepton_p": "p_{l, lead} [GeV]",
    "leading_zll_lepton_theta": "#theta_{l, lead}",
    "subleading_zll_lepton_p": "p_{l, sub} [GeV]",
    "subleading_zll_lepton_theta": "#theta_{l, sub}",
    "zll_leptons_acolinearity": "Acolinearity(l_{1}, l_{2})",
    "zll_leptons_acoplanarity": "Acoplanarity(l_{1}, l_{2})",

    # Higgs & Jets
    "higgs_m": "m_{jj} [GeV]",
    "jet1_p": "p_{j1} [GeV]",
    "jet1_theta": "#theta_{j1}",
    "jet1_phi": "#phi_{j1}",
    "jet1_mass": "m_{j1} [GeV]",
    "jet1_E": "E_{j1} [GeV]",
    "jet1_nconst": "N_{const, j1}",
    "jet2_p": "p_{j2} [GeV]",
    "jet2_theta": "#theta_{j2}",
    "jet2_phi": "#phi_{j2}",
    "jet2_mass": "m_{j2} [GeV]",
    "jet2_E": "E_{j2} [GeV]",
    "jet2_nconst": "N_{const, j2}",
    "event_d12": "d_{12}",
    "event_d23": "d_{23}",
    "event_d34": "d_{34}",
    "event_d45": "d_{45}",

    # Flavor Tagging Scores
    "jet1_btag": "j_{1} b-tag score",
    "jet2_btag": "j_{2} b-tag score",
    "jet1_stag": "j_{1} s-tag score",
    "jet2_stag": "j_{2} s-tag score",
    "jet1_ctag": "j_{1} c-tag score",
    "jet2_ctag": "j_{2} c-tag score",
    "jet1_utag": "j_{1} u-tag score",
    "jet2_utag": "j_{2} u-tag score",
    "jet1_dtag": "j_{1} d-tag score",
    "jet2_dtag": "j_{2} d-tag score",
    "jet1_Gtag": "j_{1} g-tag score",
    "jet2_Gtag": "j_{2} g-tag score",
    "jet1_tautag": "j_{1} #tau-tag score",
    "jet2_tautag": "j_{2} #tau-tag score",
    "btag_max": "max b-tag score",
    "stag_other": "other s-tag score",

    # Gen-level Info & Flags
    "is_Hbs": "Signal Flag (H#rightarrow bs)",
    "gen_b_p": "p_{b, gen} [GeV]",
    "gen_b_theta": "#theta_{b, gen}",
    "gen_b_phi": "#phi_{b, gen}",
    "gen_b_pdg": "PDG ID_{b, gen}",
    "gen_s_p": "p_{s, gen} [GeV]",
    "gen_s_theta": "#theta_{s, gen}",
    "gen_s_phi": "#phi_{s, gen}",
    "gen_s_pdg": "PDG ID_{s, gen}",

    # Unnormalized BDT Scores
    "BDTscore_class0": "BDT Score (Class 0)",
    "BDTscore_class1": "BDT Score (Class 1)",
    "BDTscore_class2": "BDT Score (Class 2)",
    "BDTscore_class3": "BDT Score (Class 3)",
    "BDTscore_class4": "BDT Score (Class 4)",
    "BDTscore_class5": "BDT Score (Class 5)",
    "BDTscore_class6": "BDT Score (Class 6)",
    "BDTscore_class7": "BDT Score (Class 7)",

    # Normalized BDT Probabilities
    "norm_prob0": "Normalized Prob (Class 0)",
    "norm_prob1": "Normalized Prob (Class 1)",
    "norm_prob2": "Normalized Prob (Class 2)",
    "norm_prob3": "Normalized Prob (Class 3)",
    "norm_prob4": "Normalized Prob (Class 4)",
    "norm_prob5": "Normalized Prob (Class 5)",
}

xlims = {
    # MET & Missing Kinematics
    "met_p": (0, 50),
    "met_pt": (0, 50),
    "met_theta": (0, np.pi),
    "met_phi": (-np.pi, np.pi),
    "met_px": (-50, 50),
    "met_py": (-50, 50),
    "met_pz": (-60, 60),
    "higgs_met_m": (100, 140),
    "higgs_met_e": (100, 140),
    "cosTheta_miss": (-1.0, 1.0),

    # Total Mass & Energy (Center of mass = 240 GeV)
    "total_m": (180, 250),
    "total_e": (210, 245),

    # Z Leptonic & Leptons
    "zll_m": (86, 96),
    "zll_p": (20, 70),
    "zll_theta": (0, np.pi),
    "zll_recoil_m": (120, 140),
    "leading_zll_lepton_p": (20, 90),
    "leading_zll_lepton_theta": (0, np.pi),
    "subleading_zll_lepton_p": (10, 70),
    "subleading_zll_lepton_theta": (0, np.pi),
    "zll_leptons_acolinearity": (0, np.pi),
    "zll_leptons_acoplanarity": (0, np.pi),

    # Higgs Candidate & Jet Kinematics
    "higgs_m": (100, 140),
    "jet1_p": (10, 90),
    "jet1_theta": (0, np.pi),
    "jet1_phi": (-np.pi, np.pi),
    "jet1_mass": (0, 30),
    "jet1_E": (10, 90),
    "jet1_nconst": (0, 60),
    "jet2_p": (10, 80),
    "jet2_theta": (0, np.pi),
    "jet2_phi": (-np.pi, np.pi),
    "jet2_mass": (0, 25),
    "jet2_E": (10, 80),
    "jet2_nconst": (0, 60),

    # Clustering / Durham Scale Parameters (log-scale recommended for plotting)
    "event_d12": (0, 1000),
    "event_d23": (0, 100),
    "event_d34": (0, 10),
    "event_d45": (0, 2),

    # Flavor Tag Scores
    "jet1_btag": (0, 1),
    "jet2_btag": (0, 1),
    "jet1_stag": (0, 1),
    "jet2_stag": (0, 1),
    "jet1_ctag": (0, 1),
    "jet2_ctag": (0, 1),
    "jet1_utag": (0, 1),
    "jet2_utag": (0, 1),
    "jet1_dtag": (0, 1),
    "jet2_dtag": (0, 1),
    "jet1_Gtag": (0, 1),
    "jet2_Gtag": (0, 1),
    "jet1_tautag": (0, 1),
    "jet2_tautag": (0, 1),
    "btag_max": (0, 1),
    "stag_other": (0, 1),

    # Truth / Gen-level Info
    "is_Hbs": (-0.5, 1.5),
    "gen_b_p": (0, 90),
    "gen_b_theta": (0, np.pi),
    "gen_b_phi": (-np.pi, np.pi),
    "gen_b_pdg": (-6, 6),
    "gen_s_p": (0, 90),
    "gen_s_theta": (0, np.pi),
    "gen_s_phi": (-np.pi, np.pi),
    "gen_s_pdg": (-6, 6),

    # Raw BDT Scores
    "BDTscore_class0": (0, 1),
    "BDTscore_class1": (0, 1),
    "BDTscore_class2": (0, 1),
    "BDTscore_class3": (0, 1),
    "BDTscore_class4": (0, 1),
    "BDTscore_class5": (0, 1),
    "BDTscore_class6": (0, 1),
    "BDTscore_class7": (0, 1),

    # Normalized BDT Probabilities
    "norm_prob0": (0, 1),
    "norm_prob1": (0, 1),
    "norm_prob2": (0, 1),
    "norm_prob3": (0, 1),
    "norm_prob4": (0, 1),
    "norm_prob5": (0, 1),
}

for var in branches:
    fig, ax = plt.subplots()

    low_lim, high_lim = xlims[var]

    if var == "btag_max" or var == "stag_other" or var == "met_theta":
        bins = np.linspace(low_lim, high_lim, 50)
    else:
        bins = np.arange(low_lim, high_lim + 0.5, 0.5)
    
    if var.startswith("BDTscore") or var.startswith("norm"):
        bins = np.linspace(low_lim, high_lim, 50)

    for name, d in data.items():
        ax.hist(d[var], bins=bins, range=(low_lim, high_lim),
                density=True, histtype="step",
                label=name, color=colors[name])

    ax.set_xlim(*xlims[var])
    ax.set_xlabel(labels[var])
    ax.set_ylabel("Normalised to unit area")
    ax.legend(fontsize=7)
    fig.savefig(f"{outdir}{var}_normalised.png")
    plt.close(fig)


#Cutflow
cutflow = {name: [] for name in data}

#Create mask and layer for each cut
for name, d in data.items():
    mask = np.ones(len(d[branches[0]]), dtype=bool)

    # Raw Events
    cutflow[name].append(mask.sum())  

    #Z-momentum cut
    mask &= (d["zll_p"] > 20) & (d["zll_p"] < 70)
    cutflow[name].append(mask.sum())

    #Cut on Z- mass
    mask &= (d["zll_m"] > 86) & (d["zll_m"] < 96)
    cutflow[name].append(mask.sum())

    #Cut on Recoil mass
    mask &= (d["zll_recoil_m"] > 120) & (d["zll_recoil_m"] < 140)
    cutflow[name].append(mask.sum())

steps = ["Preselection", "Z-Momentum Cut", "Z-Mass Cut", "Recoil Cut"]

#Total Decay Cutflow

fig, ax = plt.subplots(figsize=(8, 5))

#Loop and plot dictionary
# for name, counts in cutflow.items():
#     ax.plot(steps, counts, marker='o', label=name, color=colors[name], linewidth=2)

# Loop and plot percentages relative to Preselection
for name, counts in cutflow.items(): 
    initial_events = counts[0]
    if initial_events > 0:
        percentages = [(c / initial_events) * 100 for c in counts]
    else:
        percentages = [0] * len(counts)
        
    ax.plot(steps, percentages, marker='o', label=name, color=colors[name], linewidth=2)

ax.set_yscale("linear")
ax.set_ylabel("Percentage of Surviving Events")
ax.set_xlabel("Selection Stage")
ax.set_title("Analysis Cutflow Comparison")
ax.grid(True, which="both", linestyle="--", alpha=0.5)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

plt.tight_layout()
fig.savefig(f"{outdir}total_cutflow_plot.png")
fig.savefig(f"{outdir}total_cutflow_plot.pdf")
plt.close(fig)

print("Total Cutflow plot successfully generated!")

#Total Decay Cutflow with relative percentages

fig, ax = plt.subplots(figsize=(8, 5))

# Loop through each sample/process in your cutflow dictionary
for name, counts_list in cutflow.items(): 
    percentages = []
    
    # Initialize previous_step to the first cut of THIS specific sample
    previous_step = counts_list[0] if len(counts_list) > 0 else 0
    
    for c in counts_list:
        if previous_step > 0:
            pct = (c / previous_step) * 100
            percentages.append(pct)
        else:
            percentages.append(0.0)
            
        # Update previous_step to the current step for the next iteration
        previous_step = c
        
    # Plot the full line for this sample
    ax.plot(steps, percentages, marker='o', label=name, color=colors[name], linewidth=2)

ax.set_yscale("linear")
ax.set_ylabel("Percentage of Surviving Events")
ax.set_xlabel("Selection Stage")
ax.set_title("Analysis Cutflow Comparison")
ax.grid(True, which="both", linestyle="--", alpha=0.5)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

plt.tight_layout()
fig.savefig(f"{outdir}relative%_cutflow_plot.png")
fig.savefig(f"{outdir}relative%_cutflow_plot.pdf")
plt.close(fig)

print("Total Cutflow plot successfully generated!")


#Higgs Decays Cutflow Plot

# higgs_decays = [
#     "H→bs (Signal)", "H→bb (Signal)", "H→bd (Signal)", 
#     "H→cu (Signal)", "H→sd (Signal)", "H→ss", "H→bb (final_state)"
# ]

higgs_decays = [
    # Off-Diagonal Higgs Decays (Signals)
    "H→bs (Signal)",
    "H→bd (Signal)",
    "H→cu (Signal)",
    "H→sd (Signal)",

    # Diagonal Higgs Decays
    "H→bb",
    "H→ss",
    "H→cc",
    "H→dd",
    "H→uu",
]

fig, ax = plt.subplots(figsize=(8, 5))

#Loop and plot dictionary
# for name, counts in cutflow.items():
#     ax.plot(steps, counts, marker='o', label=name, color=colors[name], linewidth=2)

# Loop and plot percentages relative to Preselection
for name, counts in cutflow.items(): 
    if name not in higgs_decays:
        continue
    initial_events = counts[0]
    if initial_events > 0:
        percentages = [(c / initial_events) * 100 for c in counts]
    else:
        percentages = [0] * len(counts)
        
    ax.plot(steps, percentages, marker='o', label=name, color=colors[name], linewidth=2)

ax.set_yscale("linear")
ax.set_ylabel("Percentage of Surviving Events")
ax.set_xlabel("Selection Stage")
ax.set_title("Analysis Cutflow Comparison")
ax.grid(True, which="both", linestyle="--", alpha=0.5)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

plt.tight_layout()
fig.savefig(f"{outdir}higgs_cutflow_plot.png")
plt.close(fig)

print("Higgs Cutflow plot successfully generated!")


#Non-Higgs Backgrounds

other_backgrounds = [
    # Other Higgs Decays
    "H→WW",
    "H→ZZ (noInv)",
    "H→ττ",
    "H→Zγ",
    "H→gg",

    # Non-Higgs SM Backgrounds
    "ZH (inclusive)",
    "ZZ",
    "WW (inclusive)",
    "Z/γ→μμ",
    "eγ→eZ→μμ",
    "γe→eZ→μμ",
    "γγ→μμ",
]

fig, ax = plt.subplots(figsize=(8, 5))

#Loop and plot dictionary
# for name, counts in cutflow.items():
#     ax.plot(steps, counts, marker='o', label=name, color=colors[name], linewidth=2)

# Loop and plot percentages relative to 'Raw Events'
for name, counts in cutflow.items():
    if name not in other_backgrounds:
        continue
    initial_events = counts[0]
    if initial_events > 0:
        percentages = [(c / initial_events) * 100 for c in counts]
    else:
        percentages = [0] * len(counts)
        
    ax.plot(steps, percentages, marker='o', label=name, color=colors[name], linewidth=2)

ax.set_yscale("linear")
ax.set_ylabel("Percentage of Surviving Events")
ax.set_xlabel("Selection Stage")
ax.set_title("Analysis Cutflow Comparison")
ax.grid(True, which="both", linestyle="--", alpha=0.5)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8) # Push legend outside

plt.tight_layout()
fig.savefig(f"{outdir}other_background_cutflow_plot.png")
plt.close(fig)

print("Other Background Cutflow plot successfully generated!")


#Table
fig, ax = plt.subplots(figsize=(16, 6))  # 1. Increased figure width (12 -> 16)
ax.axis('off')

steps = ["Preselection", "Z-Mass Cut", "Z-Momentum Cut", "Recoil Cut"]

table_data = [] 
for name, counts in cutflow.items():
    initial_events = counts[0]
    row = [name]
    for c in counts:
        pct = (c / initial_events * 100) if initial_events > 0 else 0.0
        row.append(f"{c}\n({pct:.2f}%)")
    table_data.append(row)

col_labels = ["Sample"] + steps

# 2. Calculate explicit, generous column widths
# Give the "Sample" column more space (e.g., 35% of width) and split the rest evenly
num_cols = len(col_labels)
col_widths = [0.32] + [0.17] * (num_cols - 1) 

table = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    colWidths=col_widths, # 3. Pass the explicit widths here
    loc='center',
    cellLoc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(9) # Slightly larger font since we have more room now

# 4. Scale the row heights (1.8x) so the stacked text doesn't overflow vertically
table.scale(1, 1.8) 

# 5. Apply a tight layout with padding so edges don't get clipped
plt.tight_layout(pad=2.0)

fig.savefig(f"{outdir}cutflow_table.png", bbox_inches='tight', dpi=150)
plt.close(fig)