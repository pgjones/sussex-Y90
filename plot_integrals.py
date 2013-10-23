#!/usr/bin/env python
#
# plot_measurements.py
#
# Extract data from a hdf5 file and plot the summed pulse heights
#
# Author P G Jones - 2013-09-20 <p.g.jones@qmul.ac.uk> : First revision
##################################################################################
import ROOT
import utils
import sys
import root_utils

file_path = stripfile=sys.argv[1][:len(sys.argv[1])-5]
results = utils.HDF5File(file_path, 2)
results.load()
data = { 1 : results.get_data(1), 2 : results.get_data(2) }

print file_path, "Meta data:"
print "Trigger:", results.get_meta_data("trigger")
print "Y Scale ch1:", results.get_meta_data("ch1_y_scale")

int_1 = ROOT.TH1D("int1", "int", 1000, -1e-8, 1e-8)
int_2 = ROOT.TH1D("int2", "int", 1000, -1e-8, 1e-8)
units = (results.get_meta_data("unit"), "count")

num_events = 0
for ch1, ch2 in zip(data[1], data[2]):
    num_events += 1
    if -ch1 > 1e-8:
        print "balls"
    int_1.Fill(-ch1)
    int_2.Fill(-ch2)

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
