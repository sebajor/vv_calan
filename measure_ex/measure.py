from vv_calan import vv_calan
import argparse
import calandigital as calan
import time, os

parser = argparse.ArgumentParser(
    description="start save data")
parser.add_argument("-i", "--ip", dest="ip", default=None,
        help="ROACH IP address.")
parser.add_argumnet("-v", "--valon", dest="valon_freq", default=1080,
        help="Valon frequency")
parser.add_argument("-f", "--freq", dest="freq2save", type=float, default=60.01,
        help="Frequency to acquire")
parser.add_argument("-n" "--filename", dest="savefile", default=None,
        help="filename to save data")
parser.add_argument("-t","--savetime", dest="savetime", default=2, 
        help="Time to save (in minutes)")
parser.add_argument("-m", "--my_ip", dest="my_ip", default="10.0.0.1",
        help="Your computer IP (must be visible for the roach")
parser.add_argument("-c", "--clean", dest=clean, action="store_true", 
        help="delete the rawdata after parsing it")

def main():
    args = parser.parse_args()
    roach = vv_calan(args.ip, "", args.valon_freq)
    chan2save = roach.get_index(args.freq2save)
    print('Looking at channel: '+str(chann2save))
    roach.init_chann_acq(channel_index)
    roach.ppc_upload_code()
    roach.ppc_meas(chann=channel_index)
    while(roach.ppc_check_status() ==1):
        time.sleep(1)
    roach.ppc_download_data(pc_IP=args.my_ip)
    time.sleep(1)
    roach.parse_raw_data('raw_data', out_name=args.savefile)
    if(args.clean):
        os.rmdir('raw_data')
    
if __name__ == '__main__':
    main()


