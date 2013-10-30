#!/usr/bin/env python
#
# plot_waveform_coincidence_timing.py
#
# Extract data from a hdf5 file and plot the timing distribution between the channels.
#
# Author P G Jones - 2013-10-30 <p.g.jones@qmul.ac.uk> : First revision
##################################################################################
import ROOT
import utils
import sys
import root_utils

def get_trigger_time(hist, trigger=0.0):
    """Return the time that the trigger is first reached."""
    return hist.FindFirstBinAbove(trigger)

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }
timeform_1 = results.get_meta_data("ch1_timeform")
timeform_2 = results.get_meta_data("ch2_timeform")

print file_path, "Meta data:"
print "Trigger:", results.get_meta_data("trigger")

time = ROOT.TH1D("int1", "int", 1000, 0.0, 1000.0)
units = ("count", "ns")

num_events = 0
for ch1, ch2 in zip(data[1], data[2]):
    num_events += 1
    hist_1 = root_utils.waveform_to_hist(timeform_1, ch1, units)
    hist_2 = root_utils.waveform_to_hist(timeform_2, ch2, units)
    hist_2.SetLineColor(ROOT.kRed)
    start_time = get_trigger_time(hist_1, 0.1)
    end_time = get_trigger_time(hist_2, 0.01)
    time.Fill(end_time - start_time)

print "Loaded %i events" % num_events

c1 = ROOT.TCanvas()
time.Draw()
c1.SetLogy()
raw_input("end")
