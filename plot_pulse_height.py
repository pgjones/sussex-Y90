#!/usr/bin/env python
#
# plot_pule_height.py
#
# Extract data from a hdf5 file and plot the pulse heights
#
# Author P G Jones - 2013-09-16 <p.g.jones@qmul.ac.uk> : First revision
##################################################################################
import ROOT
import utils
import sys
import root_utils

int_1 = ROOT.TH1D("int1", "int", 200, -0.1, 0.5)
int_2 = ROOT.TH1D("int2", "int", 200, -0.1, 0.5)
units = ("s", "volts")

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }
timeform_1 = results.get_meta_data("ch1_timeform")
timeform_2 = results.get_meta_data("ch2_timeform")

num_events = 0
for ch1, ch2 in zip(data[1], data[2]):
    num_events += 1
    hist_1 = root_utils.waveform_to_hist(timeform_1, ch1, units)
    hist_2 = root_utils.waveform_to_hist(timeform_2, ch2, units)
    hist_2.SetLineColor(ROOT.kRed)
    zero_bin = hist_1.GetXaxis().FindBin(0.0)
    max_1 = 0.0
    max_2 = 0.0
    for iBin in range(zero_bin - 20, zero_bin + 20):
        max_1 = max(hist_1.GetBinContent(iBin), max_1)
        max_2 = max(hist_2.GetBinContent(iBin), max_2)
    int_1.Fill(max_1)
    int_2.Fill(max_2)

print "Loaded %i events" % num_events

c1 = ROOT.TCanvas()
int_1.Draw()
int_2.SetLineColor(ROOT.kRed)
int_2.Draw("SAME")
int_1.GetYaxis().SetRangeUser(0.1, max(int_1.GetMaximum(), int_2.GetMaximum()))
c1.Update()
c1.SetLogy()
raw_input("end")
