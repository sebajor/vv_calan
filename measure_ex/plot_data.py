from vv_calan import vv_calan
import argparse, time
import calandigital as calan

parser = argparse.ArgumentParser(
    description="Plot spectra from an spectrometer model in ROACH.")
parser.add_argument("-i", "--ip", dest="ip", default=None,
    help="ROACH IP address.")
parser.add_argument("-b", "--boffile", dest="bof", default=None,
        help="boffile")
parser.add_argument("-bw", "--bw", dest="bw", default=135.)

parser.add_argument("-fi", "--fi", dest="fi", default=0,
        help="Init frequency for the plots")

parser.add_argument("-fe", "--fe", dest="fe", default=67.5,
        help="End frequency for the plots")

parser.add_argument("-s", "--spec", dest="spect", action="store_true",
        help="plot spectra of the inputs")

parser.add_argument("-c", "--corr", dest="correlator", action="store_true",
        help="plot correlation of the inputs")

parser.add_argument("-ph", "--phase", dest="phase", action="store_true",
        help="plot phase between the inputs")

parser.add_argument("-f", "--freq", dest="freq2save", type=float, default=60.01,
        help="Frequency to acquire")

parser.add_argument("-p", "--point",dest="pt_vals", action="store_true",
        help="plot point values, needs the -f parameter")

def main():
    args = parser.parse_args()
    fs = args.bw*8
    roach = vv_calan(args.ip, args.bof, fs)
    time.sleep(0.5)
    opts = []
    if(args.spect):
        opts.append('spect0')
        opts.append('spect1')
    if(args.correlator):
        opts.append('correlation')
    if(args.phase):
        opts.append('phase')
    if(args.pt_vals):
        opts.append('chann_values')

    chann2save = roach.get_index(float(args.freq2save))
    print('Looking at channel: '+str(chann2save))
    roach.create_plot()
    roach.generate_plot(plots=opts, freq=[float(args.fi), float(args.fe)], chann=chann2save)


if __name__ == '__main__':
    main()

