import ROOT
import os
import sys

# Locate the FCCWorkplace checkout so the paths below follow the repo, not a
# particular user area (override with FCCWORKPLACE_ROOT).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repo_paths import analysis_path


# global parameters
intLumi        = 10.8e+06 #in pb-1
ana_tex        = 'e^{+}e^{-} #rightarrow ZH #rightarrow #mu^{+}#mu^{-} + X'
delphesVersion = '3.4.2'
energy         = 240.0
collider       = 'FCC-ee'
# NB: do_plots concatenates inputDir + "<process>_<sel>_histo.root" without a
# separator, so the trailing one is required.
inputDir       = analysis_path("Histo_Files") + os.sep
yaxis          = ['lin','log']
#yaxis          = ['lin']
stacksig       = ['stack','nostack']
#stacksig       = ['stack']
formats        = ['png'] #['pdf','png','eps','tex']

#yaxis          = ['lin']
outdir         = analysis_path("Final_Plots")

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
                #met
                "higgs_met_m", "higgs_met_e",
                "met_p", "met_pt", "met_theta", "met_phi",
                "total_m", "total_e",
               ]
###Dictonary with the analysis name as a key, and the list of selections to be plotted for this analysis. The name of the selections should be the same than in the final selection
selections = {}
selections['ZH']   =["No_Cuts",
                     "sel_Baseline_no_costhetamiss"
                     ]

extralabel = {}
extralabel["sel_Baseline_no_costhetamiss"]            = "Baseline without cos#theta_{miss} cut"   
extralabel["No_Cuts"]            = "Baseline without any cuts"   


colors = {}
colors['mumuH'] = ROOT.kRed
colors['eeH'] = ROOT.kRed
colors['Zmumu'] = ROOT.kCyan
colors['Zee'] = ROOT.kCyan
colors['eeZ'] = ROOT.kSpring+10
colors['WWmumu'] = ROOT.kBlue+1
colors['WWee'] = ROOT.kBlue+1
colors['gagamumu'] = ROOT.kBlue-8
colors['gagaee'] = ROOT.kBlue-8
colors['WW'] = ROOT.kBlue+1
colors['ZZ'] = ROOT.kGreen+2
colors['mumuH_bs'] = ROOT.kMagenta
colors['mumuH_bb'] = ROOT.kOrange+7
colors['mumuH_ss'] = ROOT.kViolet

plots = {}
plots['ZH'] = {'signal':{'mumuH_bs':['wzp6_ee_mumuH_Hbs_W4p1MeV_ecm240']},
               'backgrounds':{'mumuH':['wzp6_ee_mumuH_ecm240'],
                              'mumuH_bb':['wzp6_ee_mumuH_Hbb_ecm240'],
                              'mumuH_ss':['wzp6_ee_mumuH_Hss_ecm240'],
                              
                              'WWmumu':['p8_ee_WW_mumu_ecm240'],
                              'WW':['p8_ee_WW_ecm240'],
                              'ZZ':['p8_ee_ZZ_ecm240'],
                              'Zmumu':['wzp6_ee_mumu_ecm240'],
                              'eeZ':["wzp6_egamma_eZ_Zmumu_ecm240",
                              "wzp6_gammae_eZ_Zmumu_ecm240"],
                              'gagamumu':["wzp6_gaga_mumu_60_ecm240"]
                              },
              }

legend = {}
legend['mumuH_bs'] = 'Z(#mu^{-}#mu^{+})H(b#bar{s})'
legend['mumuH_bb'] = 'Z(#mu^{-}#mu^{+})H(b#bar{b})'
legend['mumuH_ss'] = 'Z(#mu^{-}#mu^{+})H(s#bar{s})'
legend['mumuH'] = 'Z(#mu^{-}#mu^{+})H'
legend['eeH'] = 'Z(e^{-}e^{+})H'
legend['Zmumu'] = 'Z/#gamma#rightarrow #mu^{+}#mu^{-}'
legend['Zee'] = 'Z/#gamma#rightarrow e^{+}e^{-}'
legend['eeZ'] = 'e^{+}(e^{-})#gamma'
legend['WWmumu'] = 'W^{+}(#nu_{#mu}#mu^{+})W^{-}(#bar{#nu}_{#mu}#mu^{-})'
legend['WWee'] = 'W^{+}(#nu_{e}e^{+})W^{-}(#bar{#nu}_{e}e^{-})'
legend['gagamumu'] = '#gamma#gamma#rightarrow#mu^{+}#mu^{-}'
legend['gagaee'] = '#gamma#gamma#rightarrow e^{+}e^{-}'
legend['WW'] = 'W^{+}W^{-}'
legend['ZZ'] = 'ZZ'


