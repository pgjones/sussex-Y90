#!/usr/bin/env python
#
# plot_pule_sum.py
#
# Extract data from a hdf5 file and plot the summed pulse heights
#
# Author P G Jones - 2013-09-20 <p.g.jones@qmul.ac.uk> : First revision
##################################################################################
import ROOT
import utils
import sys
import root_utils

window_low = -20
window_high = +20

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }
timeform_1 = results.get_meta_data("ch1_timeform")
timeform_2 = results.get_meta_data("ch2_timeform")

ymult = results.get_meta_data("ch1_YMULT")
#numpy.iinfo("data type").max()
domain = ( -256.0 * ymult, 256.0 * ymult * (window_high - window_low))

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
    sum_1 = 0.0
    sum_2 = 0.0
    for iBin in range(zero_bin + window_low, zero_bin + window_high):
        sum_1 += hist_1.GetBinContent(iBin)
        sum_2 += hist_2.GetBinContent(iBin)
    int_1.Fill(sum_1)
    int_2.Fill(sum_2)

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
