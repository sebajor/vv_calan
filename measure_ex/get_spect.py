import vv_calan, time
import numpy as np
import matplotlib.pyplot as plt
import h5py

n_spects = 2**10
n_channels = 8192

roachIP = '192.168.1.10'
boffile = 'vv_casper_v2.bof.gz'
valon_freq = 1080

acc_time = 1.2*10**-3    ##1.2 ms
freq2save = 60.01          ##mhz
duration = 5           #minutes

roach = vv_calan.vv_calan(bof_path=boffile,roachIP=roachIP, valon_freq=valon_freq )
time.sleep(0.5)
roach.upload_bof()
time.sleep(1)

print("intializing vector voltmeter and timestamp")
roach.init_vv(acc_time)

powa = np.zeros([n_spects, n_channels])
powb = np.zeros([n_spects, n_channels])
phase = np.zeros([n_spects, n_channels])

for i in range(n_spects):
    print(i)
    powa[i,:] = roach.get_adc0_spect()
    powb[i,:] = roach.get_adc1_spect()
    phase[i,:] = roach.get_rel_phase()


np.savetxt('powa',powa)
np.savetxt('powb', powb)
np.savetxt('phase',phase)


