import os

repo = "/usfcc/u/asmith4/Code/FCCWorkplace/analysis/Hbs/mumu"

class loc: pass
loc.ROOT        = repo 
loc.OUT         = loc.ROOT + '/output_trained'
loc.DATA        = loc.ROOT + '/data'
loc.CSV         = loc.DATA + '/csv'
loc.PKL         = loc.DATA + '/pkl'
loc.PKL_Val     = loc.DATA + '/pkl_val'
loc.ROOTFILES   = loc.DATA + '/ROOT'
loc.PLOTS       = loc.DATA + '/plots'
loc.PLOTS_Val   = loc.OUT  + 'plots_val'
loc.TEX         = loc.OUT  + 'tex'
loc.JSON        = loc.OUT  + 'json'

loc.EOS      = repo
loc.BDT      = loc.EOS + '/BDT'
loc.PROD     = loc.EOS
loc.STAGE1   = loc.PROD + '/firstlook'
loc.TRAIN    = loc.PROD + '/temp_files'
loc.TRAIN2   = loc.PROD + '/Training_4stage2'
loc.ANALYSIS = loc.PROD + '/BDT_analysis_samples'

# BDT input variables
train_vars = [
    #MET
    # "met_p", "met_pt", "met_theta", "met_phi",
    # "met_px", "met_py", "met_pz",
    # "higgs_met_m", "higgs_met_e",
    #total E and mass
    # "total_m", "total_e",
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
    # "btag_max",  "stag_other",
]

latex_mapping = {
    "met_p":                        r"$p_{\mathrm{miss}}$",
    "met_pt":                       r"$p_{\mathrm{miss}}^{T}$",
    "met_theta":                    r"$\theta_{\mathrm{miss}}$",
    "met_phi":                      r"$\phi_{\mathrm{miss}}$",
    "met_px":                       r"$p_{x,\mathrm{miss}}$",
    "met_py":                       r"$p_{y,\mathrm{miss}}$",
    "met_pz":                       r"$p_{z,\mathrm{miss}}$",
    "higgs_met_m":                  r"$m_{H+\mathrm{miss}}$",
    "higgs_met_e":                  r"$E_{H+\mathrm{miss}}$",
    "total_m":                      r"$m_{\mathrm{total}}$",
    "total_e":                      r"$E_{\mathrm{total}}$",
    "zll_m":                        r"$m_{\ell\ell}$",
    "zll_p":                        r"$p_{\ell\ell}$",
    "zll_theta":                    r"$\theta_{\ell\ell}$",
    "zll_recoil_m":                 r"$m_{\mathrm{recoil}}$",
    "leading_zll_lepton_p":         r"$p_{\ell_1}$",
    "leading_zll_lepton_theta":     r"$\theta_{\ell_1}$",
    "subleading_zll_lepton_p":      r"$p_{\ell_2}$",
    "subleading_zll_lepton_theta":  r"$\theta_{\ell_2}$",
    "zll_leptons_acolinearity":     r"$|\Delta\theta_{\ell\ell}|$",
    "zll_leptons_acoplanarity":     r"$|\Delta\phi_{\ell\ell}|$",
    "higgs_m":                      r"$m_{jj}$",
    "jet1_p":                       r"$p_{j_1}$",
    "jet1_theta":                   r"$\theta_{j_1}$",
    "jet1_phi":                     r"$\phi_{j_1}$",
    "jet1_mass":                    r"$m_{j_1}$",
    "jet2_p":                       r"$p_{j_2}$",
    "jet2_theta":                   r"$\theta_{j_2}$",
    "jet2_phi":                     r"$\phi_{j_2}$",
    "jet2_mass":                    r"$m_{j_2}$",
    "event_d12":                    r"$d_{12}$",
    "event_d23":                    r"$d_{23}$",
    "event_d34":                    r"$d_{34}$",
    "event_d45":                    r"$d_{45}$",
    "jet1_E":                       r"$E_{j_1}$",
    "jet2_E":                       r"$E_{j_2}$",
    "jet1_nconst":                  r"$N_{\mathrm{const},j_1}$",
    "jet2_nconst":                  r"$N_{\mathrm{const},j_2}$",
    "jet1_btag":                    r"$\mathrm{btag}_{j_1}$",
    "jet2_btag":                    r"$\mathrm{btag}_{j_2}$",
    "jet1_stag":                    r"$\mathrm{stag}_{j_1}$",
    "jet2_stag":                    r"$\mathrm{stag}_{j_2}$",
    "jet1_ctag":                    r"$\mathrm{ctag}_{j_1}$",
    "jet2_ctag":                    r"$\mathrm{ctag}_{j_2}$",
    "jet1_utag":                    r"$\mathrm{utag}_{j_1}$",
    "jet2_utag":                    r"$\mathrm{utag}_{j_2}$",
    "jet1_dtag":                    r"$\mathrm{dtag}_{j_1}$",
    "jet2_dtag":                    r"$\mathrm{dtag}_{j_2}$",
    "jet1_Gtag":                    r"$\mathrm{Gtag}_{j_1}$",
    "jet2_Gtag":                    r"$\mathrm{Gtag}_{j_2}$",
    "jet1_tautag":                  r"$\tau\mathrm{tag}_{j_1}$",
    "jet2_tautag":                  r"$\tau\mathrm{tag}_{j_2}$",
    "btag_max":                     r"$\mathrm{btag}_{\max}$",
    "stag_other":                   r"$\mathrm{stag}_{\mathrm{other}}$",
}

final_states = "mumu"

# Process names mapped to file names.
# mumuH_Hbs and mumuH_Hother share the same ROOT files;
# they are split at training time via the gen-level is_Hbs branch.
mode_names = {
    # Off-Diagonal Higgs Decays (FCNC Signals)
    "mumuH_Hbs":    "wzp6_ee_mumuH_Hbs_W4p1MeV_ecm240",
    "mumuH_Hbd":    "wzp6_ee_mumuH_Hbd_W4p1MeV_ecm240",
    "mumuH_Hcu":    "wzp6_ee_mumuH_Hcu_W4p1MeV_ecm240",
    "mumuH_Hsd":    "wzp6_ee_mumuH_Hsd_W4p1MeV_ecm240",

    "mumuH_HWW":    "wzp6_ee_mumuH_HWW_ecm240",
    "mumuH_HZZ_noInv":    'wzp6_ee_mumuH_HZZ_noInv_ecm240',
    "mumuH_Htautau":    'wzp6_ee_mumuH_Htautau_ecm240',

    # Diagonal Higgs Decays
    "mumuH_Hbb":    "wzp6_ee_mumuH_Hbb_ecm240",
    "mumuH_Hss":    "wzp6_ee_mumuH_Hss_ecm240",
    "mumuH_Hcc":    "wzp6_ee_mumuH_Hcc_ecm240",
    "mumuH_Hdd":    "wzp6_ee_mumuH_Hdd_ecm240",
    "mumuH_Huu":    "wzp6_ee_mumuH_Huu_ecm240",
    "mumuH_Hgg":    "wzp6_ee_mumuH_Hgg_ecm240",
    
    "mumuH_HZa":    'wzp6_ee_mumuH_HZa_ecm240',

    # Standard Model Backgrounds
    #"mumuH":        "wzp6_ee_mumuH_ecm240",
    "ZZ":           "p8_ee_ZZ_ecm240",
    "WW":           "p8_ee_WW_ecm240",
    "Zll":          "wzp6_ee_mumu_ecm240",
    "egamma":       "wzp6_egamma_eZ_Zmumu_ecm240",
    "gammae":       "wzp6_gammae_eZ_Zmumu_ecm240",
    "gaga_mumu":    "wzp6_gaga_mumu_60_ecm240"
}
