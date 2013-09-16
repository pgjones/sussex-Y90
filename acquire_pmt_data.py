#!/usr/bin/env python
#
# acquire_pmt_data.py
#
# Acquisition of PMT data from the Sussex setup.
# Data is saved to a hdf5 file.
#
# Author P G Jones - 2013-09-16 <p.g.jones@qmul.ac.uk> : First revision
################################################################################## 
import optparse
import scopes
import scope_connections
import utils
import time
import datetime
from pyvisa.vpp43 import visa_exceptions

def acquire_pmt_data(name, acquisition_time, trigger, trigger_channel, ymult):
    """ Acquire Sussex PMT data."""
    tek_scope = scopes.Tektronix2000(scope_connections.VisaUSB())
    # First setup the scope, lock the front panel
    tek_scope.lock()
    tek_scope.set_active_channel(1)
    tek_scope.set_active_channel(2)
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    tek_scope.set_edge_trigger(trigger, trigger_channel, True) # Falling edge trigger
    tek_scope.set_channel_coupling(1, "ac")
    tek_scope.set_channel_coupling(2, "ac")
    tek_scope.set_channel_y(1, ymult)
    tek_scope.set_channel_y(2, ymult)
    tek_scope.set_data_mode(49500, 50500)
    tek_scope.lock() # Re acquires the preamble
    # Now create a HDF5 file and save the meta information
    file_name = name + "_" + str(datetime.date.today())
    results = utils.HDF5File(file_name, 2)
    results.add_meta_data("trigger", trigger)
    results.add_meta_data("trigger_channel", trigger_channel)
    results.add_meta_data("ch1_timeform", tek_scope.get_timeform(1))
    results.add_meta_data("ch2_timeform", tek_scope.get_timeform(2))
    results.add_meta_dict(tek_scope.get_preamble(1), "ch1_")
    results.add_meta_dict(tek_scope.get_preamble(2), "ch2_")

    last_save_time = time.time()
    num_events = 0
    print "Starting data taking at time", time.strftime("%Y-%m-%d %H:%M:%S")
    while time.time() - last_save_time < acquisition_time:
        tek_scope.acquire()
        num_events += 1
        try:
            results.add_data(tek_scope.get_waveform(1), 1)
            results.add_data(tek_scope.get_waveform(2), 2)
        except Exception, e:
            print "Scope died, acquisition lost."
            print e
        except visa_exceptions.VisaIOError, e:
            print "Serious death"
            time.wait(1)
        print "|",
        if num_events % 5 == 0:
            print "_",
        if time.time()-last_save_time > 60 * 60: # I.e. one hour
            results.auto_save()
            last_save_time = time.time()
    results.save()
    print "\nFinished at", time.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog name acquisition_time channel")
    parser.add_option("-t", type="float", dest="trigger", help="Trigger level", default=-0.004)
    parser.add_option("-y", type="float", dest="ymult", help="Y Mult", default=100e-3)
    (options, args) = parser.parse_args()
    if len(args) != 3:
        print "Incorrect number of arguments"
        parser.print_help()
        exit(0)
    acquire_pmt_data(args[0], int(args[1]) * 60, options.trigger, int(args[2]), options.ymult)
