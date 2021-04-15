from valon_synth import *
from collections import OrderedDict


def get_valon_status(port='/dev/ttyUSB0', synth='B'):
    synth_ = {"A" : SYNTH_A, "B" : SYNTH_B}
    lev_dict = OrderedDict()
    lev_dict[-4] = 0; lev_dict[-1] = 3; lev_dict[2] = 6; lev_dict[5] = 8
    s = Synthesizer(port)
    try:
        synth_num = synth_[synth]
    except:
        print "Synth name error."
        exit()
    synth_freq = s.get_frequency(synth_num)
    synth_levl = s.get_rf_level(synth_num)
    print "Frequency SYNTH_" + str(synth) + ": " + str(synth_freq) + "[MHz]"
    print "RF level SYNTH_"  + str(synth) + ": " + str(synth_levl) + " (" + str(lev_dict[synth_levl]) + "dBm)"
    # False = internal, True = external
    print "Reference : " + ("external" if s.get_ref_select() else "internal")
    return (s, synth_num)

def set_valon_freq(new_freq ,port='/dev/ttyUSB0', synth='B', res=10.0):
    synth_ = {"A" : SYNTH_A, "B" : SYNTH_B}
    s, synth_num = get_valon_status(port=port, synth=synth)
    s.set_frequency(synth_[synth], new_freq, chan_spacing=res)
    synth_freq = s.get_frequency(synth_num)
    print "Updated frequency SYNTH_" + str(synth) + ": " + str(synth_freq) + "[MHz]"
    s.flash()
    s.conn.close() #?

def set_valon_ref(ref='i', port='/dev/ttyUSB0', synth='B'):
    synth_ = {"A" : SYNTH_A, "B" : SYNTH_B}
    s, synth_num = get_valon_status(port=port, synth=synth)
    if(ref=='i'):
        s.set_ref_select(False)
        print("Updated reference to internal")
    if(ref=='e'):
        s.set_ref_select(True)
        print("Updated reference to external")
    s.flash()
    s.conn.close()


def set_valon_power(level=-4, port='/dev/ttyUSB0', synth='B'):
    lev_dict = OrderedDict()
    lev_dict[-4] = 0; lev_dict[-1] = 3; lev_dict[2] = 6; lev_dict[5] = 8
    synth_ = {"A" : SYNTH_A, "B" : SYNTH_B}
    s, synth_num = get_valon_status(port=port, synth=synth)
    s.set_rf_level(synth_[synth_num]) 
    s.conn.close()
    


