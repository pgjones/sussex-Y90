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
import datetime
import time
import math
from pyvisa.vpp43 import visa_exceptions

def acquire_pmt_data(name, acquisition_time, trigger, trigger_channel, y_scale):
    """ Acquire Sussex PMT data."""
    # The minimum trigger level is a 25th of the y_scale
    if math.fabs(trigger) < y_scale / 25.0:
        trigger = y_scale / 25.0
        print "Trigger changed to", trigger
    tek_scope = scopes.Tektronix2000(scope_connections.VisaUSB())
    # First setup the scope, lock the front panel
    tek_scope.lock()
    tek_scope.set_active_channel(1)
    tek_scope.set_active_channel(2)
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    tek_scope.set_edge_trigger(trigger, trigger_channel, True) # Falling edge trigger
    tek_scope.set_channel_coupling(1, "ac")
    tek_scope.set_channel_coupling(2, "ac")
    tek_scope.set_invert_channel(1)
    tek_scope.set_invert_channel(2)
    tek_scope.set_data_mode(49500, 50500)
    tek_scope.set_channel_y(1, y_scale)
    tek_scope.set_channel_y(2, y_scale)
    tek_scope.begin()
    # Now create a HDF5 file and save the meta information
    file_name = name + "_" + str(datetime.date.today())
    results = utils.HDF5File(file_name, 2)
    results.add_meta_data("trigger", trigger)
    results.add_meta_data("trigger_channel", trigger_channel)
    results.add_meta_data("ch1_timeform", tek_scope.get_timeform(1))
    results.add_meta_data("ch2_timeform", tek_scope.get_timeform(2))
    results.add_meta_dict(tek_scope.get_preamble(1), "ch1_")
    results.add_meta_dict(tek_scope.get_preamble(2), "ch2_")

    last_save_time = datetime.datetime.now()
    start_time = datetime.datetime.now()
    heartbeat = datetime.datetime.now()
    acquisition_delta = datetime.timedelta(seconds=acquisition_time)
    num_events = 0
    print "Starting data taking at time", start_time.strftime("%Y-%m-%d %H:%M:%S")
    while datetime.datetime.now() - start_time < acquisition_delta:
        tek_scope.acquire()
        num_events += 1
        try:
            results.add_data(tek_scope.get_waveform(1), 1)
            results.add_data(tek_scope.get_waveform(2), 2)
        except visa_exceptions.VisaIOError, e:
            print "Serious death"
            time.sleep(10)
        except Exception, e:
            print "Scope died, acquisition lost."
            print e
            time.sleep(10)
        if datetime.datetime.now() - heartbeat > datetime.timedelta(minutes=1):
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Acquired %i events, current frequency is %f" % (num_events, tek_scope.get_trigger_frequency())
            heartbeat = datetime.datetime.now()
        if datetime.datetime.now() - last_save_time > datetime.timedelta(minutes=10):
            results.autosave()
            last_save_time = datetime.datetime.now()
    results.save()
    print "\nFinished at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tek_scope.unlock()

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog name acquisition_time(m) channel")
    parser.add_option("-t", type="float", dest="trigger", help="Trigger level", default=-0.004)
    parser.add_option("-y", type="float", dest="ymult", help="Y Mult", default=4e-3)
    (options, args) = parser.parse_args()
    if len(args) != 3:
        print "Incorrect number of arguments"
        parser.print_help()
        exit(0)
    acquire_pmt_data(args[0], int(args[1]) * 60, options.trigger, int(args[2]), options.ymult)
