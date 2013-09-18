#!/usr/bin/env python
#
# plot_waveforms.py
#
# Extract data from a hdf5 file and plot the waveform
#
# Author P G Jones - 2013-09-18 <p.g.jones@qmul.ac.uk> : First revision
##################################################################################
import ROOT
import utils
import sys
import time
import root_utils

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }
timeform_1 = results.get_meta_data("ch1_timeform")
timeform_2 = results.get_meta_data("ch2_timeform")
units = (results.get_meta_data("ch1_XUINT"), results.get_meta_data("ch1_YUNIT"))

c1 = ROOT.TCanvas()

num_events = 0
for ch1, ch2 in zip(data[1], data[2]):
    num_events += 1
    hist_1 = root_utils.waveform_to_hist(timeform_1, ch1, units)
    hist_2 = root_utils.waveform_to_hist(timeform_2, ch2, units)
    hist_2.SetLineColor(ROOT.kRed)
    hist_1.GetYaxis().SetRangeUser(min(hist_2.GetMinimum(), hist_2.GetMinimum()), 
                                   max(hist_1.GetMaximum(), hist_2.GetMaximum()))
    hist_1.Draw()
    hist_2.Draw("SAME")
    c1.Update()
    time.sleep(1)

print "Loaded %i events" % num_events

