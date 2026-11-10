import ROOT
import os
import sys

# Locate the FCCWorkplace checkout so the paths below follow the repo, not a
# particular user area (override with FCCWORKPLACE_ROOT).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repo_paths import analysis_path


# Stacked plots of the analysis_stage1_trained_final_analysis_samples.py histograms:
#   fccanalysis plots analysis_stage1_trained_plot_analysis_samples.py
global parameters
intLumi        = 10.8e+06 #in pb-1
ana_tex        = 'e^{+}e^{-} #rightarrow #nu#bar{#nu}H #rightarrow #nu#bar{#nu} + X'
delphesVersion = '3.4.2'
energy         = 240.0
collider       = 'FCC-ee'


# NB: do_plots concatenates inputDir + "<process>_<sel>_histo.root" without a
# separator, so the trailing one is required.
inputDir       = analysis_path("Histo_Files_NN") + os.sep
yaxis          = ['lin','log']
stacksig       = ['stack','nostack']
formats        = ['png','pdf']
outdir         = analysis_path("Final_Plots_NN")

variables = [   #missing momentum
                "missing_m",
                "met_p", "met_pt", "met_theta", "met_phi",
                "cosTheta_miss",
                #Higgs candidate (dijet)
                "higgs_m", "higgs_p", "higgs_pt", "higgs_e", "higgs_theta",
                "jets_acolinearity", "jets_acoplanarity",
                #tag scores
                "btag_max", "stag_other",
                "jet1_btag", "jet2_btag",
                "jet1_stag", "jet2_stag",
                "jet1_ctag", "jet2_ctag",
                "jet1_utag", "jet2_utag",
                "jet1_dtag", "jet2_dtag",
                "jet1_Gtag", "jet2_Gtag",
                "jet1_tautag", "jet2_tautag",
                #jet kinematics & merging scales
                "jet1_p", "jet2_p",
                "jet1_E", "jet2_E",
                "jet1_mass", "jet2_mass",
                "jet1_theta", "jet2_theta",
                "jet1_phi", "jet2_phi",
                "jet1_nconst", "jet2_nconst",
                "event_d12", "event_d23", "event_d34", "event_d45",
                #multi-class NN output scores (BDT branch names, see apply_nn.py)
                "BDTscore_class0", "BDTscore_class1", "BDTscore_class2", "BDTscore_class3",
                "BDTscore_class4", "BDTscore_class5", "BDTscore_class6", "BDTscore_class7",
                #multi-class NN normalized probabilities
                "norm_prob0", "norm_prob1", "norm_prob2", "norm_prob3", "norm_prob4", "norm_prob5",
               ]

selections = {}
selections['nunuH'] = ["No_Cuts",
                       "APC_Cuts"
                      ]

colors = {}

# Off-Diagonal Higgs Decays (FCNC Signals)
colors['nunuH_Hbs']       = ROOT.kMagenta
# colors['nunuH_Hbd']       = ROOT.kPink + 9
# colors['nunuH_Hcu']       = ROOT.kViolet - 4
# colors['nunuH_Hsd']       = ROOT.kTeal - 7

# Standard Model Higgs Decays
colors['nunuH']           = ROOT.kRed
# colors['nunuH_Hbb']       = ROOT.kOrange + 7
# colors['nunuH_Hss']       = ROOT.kViolet
# colors['nunuH_Hcc']       = ROOT.kRed - 7
# colors['nunuH_Huu']       = ROOT.kOrange - 3
# colors['nunuH_Hdd']       = ROOT.kRed - 9
# colors['nunuH_Hgg']       = ROOT.kYellow + 1
# colors['nunuH_HWW']       = ROOT.kAzure + 1
# colors['nunuH_HZZ_noInv'] = ROOT.kAzure + 2
# colors['nunuH_Htautau']   = ROOT.kMagenta - 9
# colors['nunuH_HZa']       = ROOT.kTeal + 2

# Standard Model Non-Higgs Backgrounds
colors['ZZ']              = ROOT.kGreen + 2
colors['WW']              = ROOT.kBlue + 1
colors['Zqq']             = ROOT.kCyan
colors['nuenueZ']         = ROOT.kSpring + 10

plots = {}
plots['nunuH'] = {
    'signal': {
        'nunuH_Hbs': ['wzp6_ee_nunuH_Hbs_W4p1MeV_ecm240'],
        # 'nunuH_Hbd': ['wzp6_ee_nunuH_Hbd_W4p1MeV_ecm240'],
        # 'nunuH_Hcu': ['wzp6_ee_nunuH_Hcu_W4p1MeV_ecm240'],
        # 'nunuH_Hsd': ['wzp6_ee_nunuH_Hsd_W4p1MeV_ecm240'],
        # 'nunuH_Huu': ['wzp6_ee_nunuH_Huu_ecm240'],
        # 'nunuH_Hdd': ['wzp6_ee_nunuH_Hdd_ecm240'],
    },
    'backgrounds': {
        # Standard Model Higgs: the inclusive sample, or the exclusive decays
        # below instead (not both, they overlap)
        # 'nunuH_HWW':       ['wzp6_ee_nunuH_HWW_ecm240'],
        # 'nunuH_HZZ_noInv': ['wzp6_ee_nunuH_HZZ_noInv_ecm240'],
        # 'nunuH_Htautau':   ['wzp6_ee_nunuH_Htautau_ecm240'],
        # 'nunuH_Hbb':       ['wzp6_ee_nunuH_Hbb_ecm240'],
        # 'nunuH_Hss':       ['wzp6_ee_nunuH_Hss_ecm240'],
        # 'nunuH_Hcc':       ['wzp6_ee_nunuH_Hcc_ecm240'],
        # 'nunuH_Hgg':       ['wzp6_ee_nunuH_Hgg_ecm240'],
        # 'nunuH_HZa':       ['wzp6_ee_nunuH_HZa_ecm240'],
        'nunuH':           ['wzp6_ee_nunuH_ecm240'],

        # Non-Higgs Standard Model Backgrounds
        'ZZ':              ['p8_ee_ZZ_ecm240'],
        'WW':              ['p8_ee_WW_ecm240'],
        'Zqq':             ['p8_ee_Zqq_ecm240'],
        'nuenueZ':         ['wzp6_ee_nuenueZ_ecm240'],
    },
}

legend = {}
extralabel = {}
extralabel["APC_Cuts"]                = ""
extralabel["No_Cuts"]                 = ""

# --- Shortened Legend Labels ---

# Off-Diagonal Higgs Decays (FCNC Signals)
legend['nunuH_Hbs']       = 'H #rightarrow bs'
legend['nunuH_Hbd']       = 'H #rightarrow bd'
legend['nunuH_Hcu']       = 'H #rightarrow cu'
legend['nunuH_Hsd']       = 'H #rightarrow sd'
legend['nunuH_Huu']       = 'H #rightarrow uu'
legend['nunuH_Hdd']       = 'H #rightarrow dd'

# Standard Model Higgs Decays
legend['nunuH_HWW']       = 'H #rightarrow WW*'
legend['nunuH_HZZ_noInv'] = 'H #rightarrow ZZ*'
legend['nunuH_Htautau']   = 'H #rightarrow #tau#tau'
legend['nunuH_Hbb']       = 'H #rightarrow bb'
legend['nunuH_Hss']       = 'H #rightarrow ss'
legend['nunuH_Hcc']       = 'H #rightarrow cc'
legend['nunuH_Hgg']       = 'H #rightarrow gg'
legend['nunuH_HZa']       = 'H #rightarrow Z#gamma'

# Standard Model Non-Higgs Backgrounds
legend['nunuH']           = '#nu#bar{#nu}H'
legend['ZZ']              = 'ZZ'
legend['WW']              = 'WW'
legend['Zqq']             = 'Z/#gamma* #rightarrow q#bar{q}'
legend['nuenueZ']         = '#nu_{e}#bar{#nu}_{e}Z'
