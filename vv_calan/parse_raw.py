import struct 
import numpy as np
import datetime
import h5py


def parse_raw(raw_file, n_readings, out_name=None):
    if(out_name is None):
        filename = str(datetime.datetime.now())
    else:
        filename = out_name
    with h5py.File((filename+'.hdf5'), 'w') as f:
        pow0 = f.create_dataset('pow0', (n_readings*8192,), dtype='Q')
        pow1 = f.create_dataset('pow1', (n_readings*8192,), dtype='Q')
        re = f.create_dataset('corr_re', (n_readings*8192,), dtype='q')
        im = f.create_dataset('corr_im', (n_readings*8192,), dtype='q')
        sec = f.create_dataset('seconds', (n_readings*8192,), dtype='I')
        frac_sec = f.create_dataset('frac_sec', (n_readings*8192,), dtype='I')
        raw_data = file(raw_file, 'r')
        for i in range(n_readings):
            try:
                a2_data = np.array(struct.unpack('>8192Q', raw_data.read(8192*8)))
                b2_data = np.array(struct.unpack('>8192Q', raw_data.read(8192*8)))
                phase = np.array(struct.unpack('>16384q', raw_data.read(8192*16)))
                re_data = phase[::2];   im_data = phase[1::2]
                time = np.array(struct.unpack('>16384I', raw_data.read(8192*8)))
                sec_data = time[::2]
                frac_data = time[1::2]
                pow0[8192*i:8192*(i+1)] = a2_data
                pow1[8192*i:8192*(i+1)] = b2_data
                re[8192*i:8192*(i+1)] = re_data
                im[8192*i:8192*(i+1)] = im_data
                sec[8192*i:8192*(i+1)] = sec_data
                frac_sec[8192*i:8192*(i+1)] = frac_data
            except:
                print('There is a problem in the iteration %i'%i)
                print('Check the size of your file, we parse %f MB'%(i*8192*8.*5)/2**20)
                break
        raw_data.close()
        


def get_num_readings(filename):
    #TODO
    return 1
