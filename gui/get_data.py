import numpy as np
import struct


def get_spect0(fpga):
    """Returns the real time spectrum of the ADC0
    """
    spect0 = np.array(struct.unpack('>8192Q',fpga.read('1_A2', 8192*8)))
    spect0 = 10*np.log10(spect0+1)
    return spect0


def get_spect1(fpga):
    """Returns the real time spectrum of the ADC1
    """
    spect1 = np.array(struct.unpack('>8192Q', fpga.read('1_B2', 8192*8)))
    spect1 = 10*np.log10(spect1+1)
    return spect1


def get_corr_re(fpga):
    """Returns the real time correlation between ADC0 and ADC1
    """
    corr_re = np.array(struct.unpack('>8192q',fpga.read('AB_re', 8192*8)))
    return corr_re

def get_corr_im(fpga):
    corr_im = np.array(struct.unpack('>8192q',fpga.read('AB_im', 8192*8)))
    return corr_im


def get_phase(fpga):
    """Returns the relative phase between the ADC0 and ADC1
       for each FFT channel
    """
    corr_re = get_corr_re(fpga)
    corr_im = get_corr_im(fpga)
    phase = np.rad2deg(np.arctan2(corr_im, corr_re))
    return phase


def init_chann_data(fpga, chann,n_samp=8192,continous=1):
    """ Initialize the logic to acquire the data of one channel
        chann: channel number to save
        n_samples: number of addresses to write 
        continous: You could select if you want to use a free running
        counter to give the addresses to the brams or use a counter
        that freeze when achieve n_samp value (Usefull if you want
        to make lab measurements, but needs to be manually reaset)

        #Carefull must be taken, when you use the map plot n_samp=1
        so if you could mess up the map if you use this function
        at the same time
    """
    fpga.write_int('addr2catch' , chann)        
    fpga.write_int('mux_sel', (not continous))
    fpga.write_int('n_points', n_samp)
    fpga.write_int('reading_data',1)
    fpga.write_int('reading_data',0)





def get_chann_data(fpga, n_points=8192):
    """ Return the power in ADC0, ADC1 and correlation of one 
        given channel.
        Before using this function you must had initialize the
        acquire system with init_chann_data
    """ 
    pow0 = np.array(struct.unpack('>'+str(n_points)+'Q', fpga.read('PowA', n_points*8)))
    pow1 = np.array(struct.unpack('>'+str(n_points)+'Q', fpga.read('PowB', n_points*8)))
    
    phase = np.array(struct.unpack('>'+str(2*n_points)+'q', fpga.read('phase', 2*n_points*8)))

    re = phase[::2]
    im = phase[1::2]
    
    return [pow0, pow1, re, im]
    










    
    
    
    
        



















    

