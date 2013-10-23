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

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }
timeform_1 = results.get_meta_data("ch1_timeform")
timeform_2 = results.get_meta_data("ch2_timeform")

ymult = results.get_meta_data("ch1_YMULT")
#numpy.iinfo("data type").max()
domain = ( -256.0 * ymult, 256.0 * ymult)

int_1 = ROOT.TH1D("int1", "int", 512, domain[0], domain[1])
int_2 = ROOT.TH1D("int2", "int", 512, domain[0], domain[1])
units = (results.get_meta_data("ch1_YUNIT"), "count")

num_events = 0
for ch1, ch2 in zip(data[1], data[2]):
    num_events += 1
    hist_1 = root_utils.waveform_to_hist(timeform_1, ch1, units)
    hist_2 = root_utils.waveform_to_hist(timeform_2, ch2, units)
    hist_2.SetLineColor(ROOT.kRed)
    zero_bin = hist_1.GetXaxis().FindBin(0.0)
    max_1 = hist_1.GetBinContent(zero_bin)
    max_2 = hist_2.GetBinContent(zero_bin)
    for iBin in range(zero_bin - 20, zero_bin + 20):
        max_1 = max(hist_1.GetBinContent(iBin), max_1)
        max_2 = max(hist_2.GetBinContent(iBin), max_2)
    int_1.Fill(max_1)
    int_2.Fill(max_2)

print "Loaded %i events" % num_events

c1 = ROOT.TCanvas()
t1 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
int_1.Draw()
t1.AddEntry(int_1, "Channel 1", "l")
t1.SetFillColor(ROOT.kWhite)
int_2.SetLineColor(ROOT.kRed)
int_2.Draw("SAME")
t1.AddEntry(int_2, "Channel 2", "l")
int_1.GetYaxis().SetRangeUser(0.1, max(int_1.GetMaximum(), int_2.GetMaximum()))
t1.Draw()
c1.Update()
c1.SetLogy()
raw_input("end")
