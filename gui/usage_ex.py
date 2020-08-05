from vv_calan import vv_calan
import numpy as np

roach_ip = '192.168.0.40'      
bofname = 'vv_casper.bof'
valon_freq = 1080       #check the valon is working at the rigth freq

roach = vv_calan(roach_ip, bofname, valon_freq) 

roach.upload_bof() 
roach.init_vv(integ_time=0.0012)   #initialize the vector voltmeter and sets the integration time.

roach.adc_snapshot()            #to look at the input of the adc


roach.create_plot()             #generate the plot object

roach.generate_plot(plots=['spect0', 'spect1'], freq=[0, 67.5]) #look at the spectrum in the freq interval
roach.generate_plot(plots=['phase'], freq=[0, 67.5]) ##idem look the relative phase



channel2save = roach.get_index(45)      ##Obtain the channel number of a given frequency in mhz

#to take a measure repeat the following lines
roach.init_chann_aqc(channel2save,n_samp=1); 
[pow0, pow1, re, im]= roach.get_chann_data()
pow_diff = 10*(np.log10(pow0)-np.log10(pow1))
phase_diff = np.rad2deg(np.arctan2(im, re))














