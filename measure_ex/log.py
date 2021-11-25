import vv_calan, time
import numpy as np
import matplotlib.pyplot as plt
import h5py

roachIP = '192.168.1.14'
boffile = 'vv_casper_v2.bof.gz'
valon_freq = 1080
your_pc_ip =  '192.168.1.20'


#hyperparmeters
acc_time = 1.2*10**-3    ##1.2 ms
freq2save = 60.          ##mhz
duration = 2           #minutes

#calibration source
gen_ip = '192.168.1.39'
gen_freq = 10           ##mhz
gen_pow = -3            ##dbm
load = 0                #if you want to load a previous calibration
load_dir = ''           #if load, the file where is contained the calibration
cal_dir = 'adc5gcal'    #the output calibration is saved with that header
manual=0                #you could set the power and freq by yourself, by default we use pyvisa


roach = vv_calan.vv_calan(bof_path=boffile,roachIP=roachIP, valon_freq=valon_freq )
time.sleep(0.5)
roach.upload_bof()
time.sleep(1)

#intialize vector voltmeter and timestamp
print("intializing vector voltmeter and timestamp")
roach.init_vv(acc_time)
#roach.init_timestamp()

print(roach.get_hour())
#check if the timestamp is locked 
print(roach.get_unlock())

channel_index = roach.get_index(freq2save)

#calibrate adcs
#roach.calibrate_adcs(gen_ip, gen_freq=gen_freq, gen_pow=gen_pow, load=load, 
#        cal_dir=cal_dir, manual=manual)

#adc time-data
#roach.adc_snapshot()

#create plot
roach.create_plot()
roach.generate_plot(plots=['spect0','spect1', 'phase'], freq=[freq2save-0.5,freq2save+0.5])

##start channel aquisition
print("Start channel aqcuisition in channel %i" %channel_index)
print("(take some time to prepare the powerpc, be patience)...")
roach.init_chann_aqc(channel_index)
roach.ppc_upload_code() #this one take some time
roach.ppc_meas(chann=channel_index, duration=duration)

running = roach.ppc_check_status()  #1 if the measurment is taking place
print("The powerpc is collecting data: %i" %running)
roach.generate_plot(plots=['chann_values','spect0','spect1', 'phase'], freq=[freq2save-0.5,freq2save+0.5], chann=channel_index) #to review the measurmetne

#to check if the process is finished
running = roach.ppc_check_status()  #1 if the measurment is still in course
#kill the process 
#roach.ppc_finish_meas()   

#when is ready you could download the data
print("the process is running: %i"%running)
ans = raw_input('Download the data [y/n] ')
if(ans=='y'):
    print("Download the data from the powerpc")
    roach.ppc_download_data(pc_IP=your_pc_ip)
    time.sleep(1)
    #parse data
    print('parse binary data')
    roach.parse_raw_data('raw_data')

##read some data, the parsed file is named with a timestamp
"""
f = h5py.File('2021-04-15 11:31:40.620943.hdf5', 'r')
keys = ['ABim', 'ABre', 'PowA', 'PowB', 'frac_sec', 'seconds']
powA = f[keys[2]][:1024]
powB = f[keys[3]][:1024]
phase = np.arctan2(keys[0][:1024],keys[1][:1024])
secs = f[keys[4]][:1024]
frac_sec = f[keys[4]][:1024]

fig = plt.figure()
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)

ax1.plot(10*np.log10(powA))
ax2.plot(10*np.log10(powB))
ax3.plot(phase)
plt.show()

"""
