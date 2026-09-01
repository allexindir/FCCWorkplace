import ROOT

global parameters
intLumi        = 10.8e+06 #in pb-1
ana_tex        = 'e^{+}e^{-} #rightarrow ZH #rightarrow #mu^{+}#mu^{-} + X'
delphesVersion = '3.4.2'
energy         = 240.0
collider       = 'FCC-ee'


inputDir       = '/usfcc/u/asmith4/Code/FCCWorkplace/analysis/Hbs/mumu/Histo_Files/'
yaxis          = ['lin','log']
stacksig       = ['stack','nostack']
formats        = ['png','pdf']
outdir         = '/usfcc/u/asmith4/Code/FCCWorkplace/analysis/Hbs/mumu/Final_Plots'

variables = [   #muons
                "leading_zll_lepton_p",
                "leading_zll_lepton_theta",
                "subleading_zll_lepton_p",
                "subleading_zll_lepton_theta",
                #Zed
                "zll_m",
                "zll_p",
                "zll_theta",
                #more control variables
                "zll_leptons_acolinearity",
                "zll_leptons_acoplanarity",
                #Recoil
                "zll_recoil_m",
                #missing Information
                "cosTheta_miss",
                #Higgs Mass
                "higgs_m",
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
                "jet1_nconst", "jet2_nconst",
                "event_d12", "event_d23", "event_d34", "event_d45",
                #met
                "higgs_met_m", "higgs_met_e",
                "met_p", "met_pt", "met_theta", "met_phi",
                "total_m", "total_e",
                #multi-class BDT raw output scores
                "BDTscore_class0", "BDTscore_class1", "BDTscore_class2", "BDTscore_class3",
                "BDTscore_class4", "BDTscore_class5", "BDTscore_class6", "BDTscore_class7",
                #multi-class BDT normalized probabilities
                "norm_prob0", "norm_prob1", "norm_prob2", "norm_prob3", "norm_prob4", "norm_prob5",
               ]

selections = {}
selections['ZH']   = ["No_Cuts",
                      "sel_Baseline_no_costhetamiss"
                     ]

# extralabel = {}
# extralabel["sel_Baseline_no_costhetamiss"] = "Baseline without cos#theta_{miss} cut"   
# extralabel["No_Cuts"]                      = "Baseline without any cuts" 

colors = {}

# Off-Diagonal Higgs Decays (FCNC Signals)
colors['mumuH_Hbs']       = ROOT.kMagenta
colors['mumuH_Hbd']       = ROOT.kPink + 9
colors['mumuH_Hcu']       = ROOT.kViolet - 4
colors['mumuH_Hsd']       = ROOT.kTeal - 7

# Standard Model Higgs Decays
colors['mumuH']         = ROOT.kRed         
# colors['mumuH_Hbb']       = ROOT.kOrange + 7
# colors['mumuH_Hss']       = ROOT.kViolet
# colors['mumuH_Hcc']       = ROOT.kRed - 7
# colors['mumuH_Hdd']       = ROOT.kRed - 9
# colors['mumuH_Huu']       = ROOT.kOrange - 3
# colors['mumuH_Hgg']       = ROOT.kYellow + 1
# colors['mumuH_HWW']       = ROOT.kAzure + 1
# colors['mumuH_HZZ_noInv'] = ROOT.kAzure + 2
# colors['mumuH_Htautau']   = ROOT.kMagenta - 9
# colors['mumuH_HZa']       = ROOT.kTeal + 2

# Standard Model Non-Higgs Backgrounds
colors['ZZ']              = ROOT.kGreen + 2
colors['WW']              = ROOT.kBlue + 1
colors['Zll']             = ROOT.kCyan
colors['egamma']          = ROOT.kSpring + 10
colors['gammae']          = ROOT.kSpring + 9
colors['gaga_mumu']       = ROOT.kBlue - 8

plots = {}
plots['ZH'] = {
    'signal': {
        'mumuH_Hbs': ['wzp6_ee_mumuH_Hbs_W4p1MeV_ecm240'],
        # 'mumuH_Hbd': ['wzp6_ee_mumuH_Hbd_W4p1MeV_ecm240'],
        # 'mumuH_Hcu': ['wzp6_ee_mumuH_Hcu_W4p1MeV_ecm240'],
        # 'mumuH_Hsd': ['wzp6_ee_mumuH_Hsd_W4p1MeV_ecm240'],
        # 'mumuH_Hdd':     ['wzp6_ee_mumuH_Hdd_ecm240'],
        # 'mumuH_Huu':     ['wzp6_ee_mumuH_Huu_ecm240'],
    },
    'backgrounds': {
        # Off-Diagonal / Standard Model Higgs Backgrounds
        # 'mumuH_HWW':     ['wzp6_ee_mumuH_HWW_ecm240'],
        # 'mumuH_HZZ_noInv': ['wzp6_ee_mumuH_HZZ_noInv_ecm240'],
        # 'mumuH_Htautau': ['wzp6_ee_mumuH_Htautau_ecm240'],
        # 'mumuH_Hbb':     ['wzp6_ee_mumuH_Hbb_ecm240'],
        # 'mumuH_Hss':     ['wzp6_ee_mumuH_Hss_ecm240'],
        # 'mumuH_Hcc':     ['wzp6_ee_mumuH_Hcc_ecm240'],
        # 'mumuH_Hgg':     ['wzp6_ee_mumuH_Hgg_ecm240'],
        # 'mumuH_HZa':     ['wzp6_ee_mumuH_HZa_ecm240'],
        'mumuH':         ['wzp6_ee_mumuH_ecm240'],

        # Non-Higgs Standard Model Backgrounds
        'ZZ':            ['p8_ee_ZZ_ecm240'],
        'WW':            ['p8_ee_WW_ecm240'],
        'Zll':           ['wzp6_ee_mumu_ecm240'],
        'egamma':        ['wzp6_egamma_eZ_Zmumu_ecm240'],
        'gammae':        ['wzp6_gammae_eZ_Zmumu_ecm240'],
        'gaga_mumu':     ['wzp6_gaga_mumu_60_ecm240'],
    },
}

legend = {}
extralabel = {}
extralabel["sel_Baseline_no_costhetamiss"]            = ""   
extralabel["No_Cuts"]            = ""

# --- Shortened Legend Labels ---

# Off-Diagonal Higgs Decays (FCNC Signals)
legend['mumuH_Hbs']       = 'H #rightarrow bs'
legend['mumuH_Hbd']       = 'H #rightarrow bd'
legend['mumuH_Hcu']       = 'H #rightarrow cu'
legend['mumuH_Hsd']       = 'H #rightarrow sd'

# Standard Model Higgs Decays
legend['mumuH_HWW']       = 'H #rightarrow WW*'
legend['mumuH_HZZ_noInv'] = 'H #rightarrow ZZ*'
legend['mumuH_Htautau']   = 'H #rightarrow #tau#tau'
legend['mumuH_Hbb']       = 'H #rightarrow bb'
legend['mumuH_Hss']       = 'H #rightarrow ss'
legend['mumuH_Hcc']       = 'H #rightarrow cc'
legend['mumuH_Hdd']       = 'H #rightarrow dd'
legend['mumuH_Huu']       = 'H #rightarrow uu'
legend['mumuH_Hgg']       = 'H #rightarrow gg'
legend['mumuH_HZa']       = 'H #rightarrow Z#gamma'

# Standard Model Non-Higgs Backgrounds
legend['mumuH']           = '#mu#mu H'
legend['ZZ']              = 'ZZ'
legend['WW']              = 'WW'
legend['Zll']             = 'Z/#gamma* #rightarrow #mu#mu'
legend['egamma']          = 'e#gamma #rightarrow eZ(#mu#mu)'
legend['gammae']          = '#gamma e #rightarrow eZ(#mu#mu)'
legend['gaga_mumu']       = '#gamma#gamma #rightarrow #mu#mu'
