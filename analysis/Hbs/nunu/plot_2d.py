import importlib.util
import os
import sys

import ROOT

# 2D (COLZ) plots of the multi-dim histograms ("cols" entries in histoList) of
# analysis_stage1_trained_final_analysis_samples.py, one canvas per process
# group. fccanalysis plots only stacks 1D histograms, so this reuses the
# inputDir/outdir/selections/plots/legend config of the 1D plot script:
#   python plot_2d.py
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "plotcfg", os.path.join(here, "analysis_stage1_trained_plot_analysis_samples.py"))
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

# histogram name -> (x title, y title); "cols" histograms carry no axis titles
variables2D = {"met_p_vs_met_theta": ("p_{miss} [GeV]", "#theta_{miss}")}

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
os.makedirs(cfg.outdir, exist_ok=True)

for ana, sels in cfg.selections.items():
    groups = {**cfg.plots[ana]['signal'], **cfg.plots[ana]['backgrounds']}
    for sel in sels:
        for var, (xtitle, ytitle) in variables2D.items():
            for group, procs in groups.items():
                hsum = None
                for proc in procs:
                    fname = f"{cfg.inputDir}{proc}_{sel}_histo.root"
                    tf = ROOT.TFile.Open(fname)
                    if not tf or tf.IsZombie():
                        print(f"missing {fname}, skipping")
                        continue
                    h = tf.Get(var)
                    h.SetDirectory(0)
                    tf.Close()
                    if hsum is None:
                        hsum = h.Clone(f"{var}_{group}_{sel}")
                        hsum.SetDirectory(0)
                    else:
                        hsum.Add(h)
                if hsum is None:
                    continue
                # final-stage histograms are normalised to 1 pb-1
                hsum.Scale(cfg.intLumi)

                c = ROOT.TCanvas("c", "", 800, 700)
                c.SetRightMargin(0.15)
                hsum.SetTitle(f"{cfg.legend.get(group, group)}, {sel};{xtitle};{ytitle}")
                hsum.Draw("COLZ")
                for fmt in cfg.formats:
                    c.SaveAs(os.path.join(cfg.outdir, f"{sel}_{var}_{group}.{fmt}"))
                c.Close()
