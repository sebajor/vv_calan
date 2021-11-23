from vv_calan import vv_calan
import argparse

parser = argparse.ArgumentParser(
    description="intialize roach")

parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-b", "--boffile", dest="bof",
    help="Boffile to load into the FPGA.")

parser.add_argument("-bw", "--bw", dest="bw", default=135.)

parser.add_argument("-u", "--upload", dest="upload", action="store_true",
    help="If used, upload .bof from PC memory (ROACH2 only).")

parser.add_argument("-v", "--vector", dest="vv_init", action="store_true",
    help="If used, initialize the vector voltmeter")

parser.add_argument("-it", "--integ", dest="integ", type=float, default=1.2*10**-3,
    help="Integration tieme.")

parser.add_argument("-t", "--time", dest="time_stamp", action="store_true",
    help="If used, initialize timestamp")

parser.add_argument("-f", "--freq", dest="freq2save", type=float, default=60.01,
        help="frequency to save")

def main():
    args = parser.parse_args()
    fs = args.bw*8
    roach = vv_calan(args.ip, args.bof, fs)
    if(args.upload):
        roach.upload_bof()
    if(args.vv_init):
        roach.init_vv(integ_time=args.integ)
    if(args.time_stamp):
        roach.init_timestamp()
    channel_index = roach.get_index(args.freq2save)
    print("saving channel: %i"%(channel_index))
    roach.init_chann_aqc(channel_index)

if __name__ == '__main__':
    main()

