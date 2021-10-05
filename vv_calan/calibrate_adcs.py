import calandigital as cd
from calandigital.adc5g_devel.ADCCalibrate import ADCCalibrate
import numpy as np
import matplotlib.pyplot as plt
import adc5g
import pyvisa, datetime, tarfile, shutil, os 

def calibrate_adcs_visa(roach_ip, gen_ip, bw, do_ogp=0, do_inl=0,gen_freq=10, gen_pow=-3,load=0,
                        load_dir='', cal_dir='adc5gcal', manual=0):
    roach = cd.initialize_roach(roach_ip)
    snapnames = ['adcsnap0','adcsnap1']
    now = datetime.datetime.now()
    caldir =cal_dir+'_' + now.strftime('%Y-%m-%d %H:%M:%S')
    if(not manual):
        rm = pyvisa.ResourceManager('@py')
        generator = rm.open_resource("TCPIP::"+gen_ip+"::INSTR")
        generator.write("freq " +str(gen_freq) + " mhz")
        generator.write("power " +str(gen_pow) + " dbm")
        generator.query("outp on;*opc?")
    
    #plot_snapshots
    snapdata_list = cd.read_snapshots(roach, snapnames, ">i1")
    snapfig, snaplines_uncal, snaplines_cal = create_snap_figure(snapnames,
            1000)
    plot_snapshots(snaplines_uncal, snapdata_list, 1000)
    snapfig.canvas.draw()
    
    #plot uncalibrated spectrums
    dBFS = 6.02*8 + 1.76 + 10*np.log10(len(snapdata_list[0])/2)
    specfig, speclines_uncal, speclines_cal = create_spec_figure(snapnames,
            bw, dBFS)
    plot_spectra(speclines_uncal, snapdata_list, bw, dBFS)
    specfig.canvas.draw()
    
    #mmcm
    perform_mmcm_calibration(roach, 0, [snapnames[0]])
    perform_mmcm_calibration(roach, 1, [snapnames[1]])
    
    if(do_ogp or do_inl):
        adccal0 = ADCCalibrate(roach=roach, roach_name="", zdok=0,
                    snapshot=snapnames[0], dir=caldir, now=now,
                    clockrate=bw)
        adccal1 = ADCCalibrate(roach=roach, roach_name="", zdok=1, 
                    snapshot=snapnames[1], dir=caldir, now=now, 
                    clockrate=bw)

        if(not load):
                    #create calibration folder
            os.mkdir(caldir)
            print("Performing ADC5G OGP calibration, ZDOK0...")
            adccal0.do_ogp(0, gen_freq, 10)
            print("done")
            print("Performing ADC5G OGP calibration, ZDOK1...")
            adccal1.do_ogp(1, gen_freq, 10)
            print("done")
        
            print("Performing ADC5G INL calibration, ZDOK0...")
            adccal0.do_inl(0)
            print("done")

            print("Performing ADC5G INL calibration, ZDOK1...")
            adccal1.do_inl(1)
            print("done")
            ##compress the calibrated data
            compress_data(caldir)
        else:
            uncompress_data(load_dir)
            #load the ogp
            print("Loading ADC5G OGP calibration, ZDOK0...")
            adccal0.load_calibrations(load_dir, 0, ['ogp'])
            print("done")
            print("Loading ADC5G OGP calibration, ZDOK1...")
            adccal1.load_calibrations(load_dir, 1, ['ogp'])
            print("done")
            
            #laod inl
            print("Loading ADC5G INL calibration, ZDOK0...")
            adccal0.load_calibrations(load_dir, 0, ['inl'])
            print("done")
            print("Loading ADC5G INL calibration, ZDOK1...")
            adccal1.load_calibrations(load_dir, 1, ['inl'])
            print("done")
            #delete the uncompressed data
            shutil.rmtree(load_dir)

    #plot calibrated data
    snapdata_list = cd.read_snapshots(roach, snapnames, ">i1")
    plot_snapshots(snaplines_cal, snapdata_list, 1000)
    snapfig.canvas.draw()

    plot_spectra(speclines_cal, snapdata_list, bw, dBFS)
    specfig.canvas.draw()
    if(not manual):
        generator.write("outp off")
        rm.close()

    print("Done with all calibrations.")
    print("Close plots to finish.")
    plt.show()


def create_snap_figure(snapnames, nsamples):
    """
    Create figure with the proper axes settings for plotting snaphots.
    """
    axmap = {1 : (1,1), 2 : (1,2), 4 : (2,2), 16 : (4,4)}
    nsnapshots = len(snapnames)
    dtype = ">i1" # harcoded adc5g 8 bit samples

    fig, axes = plt.subplots(*axmap[nsnapshots], squeeze=False)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()

    lines_uncal = []; lines_cal = []
    for snapname, ax in zip(snapnames, axes.flatten()):
        line_uncal, = ax.plot([], [], label='uncalibrated')
        line_cal,   = ax.plot([], [], label='calibrated')
        lines_uncal.append(line_uncal)
        lines_cal.append(line_cal)
        
        ax.set_xlim(0, nsamples)
        ax.set_ylim(np.iinfo(dtype).min-10, np.iinfo(dtype).max+10)
        ax.set_xlabel('Samples')
        ax.set_ylabel('Amplitude [a.u.]')
        ax.set_title(snapname)
        ax.grid()
        ax.legend()

    return fig, lines_uncal, lines_cal

def create_spec_figure(specnames, bandwidth, dBFS):
    """
    Create figure with the proper axes settings for plotting spectra.
    """
    axmap = {1 : (1,1), 2 : (1,2), 4 : (2,2), 16 : (4,4)}

    fig, axes = plt.subplots(*axmap[len(specnames)], squeeze=False)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()

    lines_uncal = []; lines_cal = []
    for specname, ax in zip(specnames, axes.flatten()):
        line_uncal, = ax.plot([], [], label='uncalibrated')
        line_cal,   = ax.plot([], [], label='calibrated')
        lines_uncal.append(line_uncal)
        lines_cal.append(line_cal)

        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS-2, 0)
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [dBFS]')
        ax.set_title(specname)
        ax.grid()
        ax.legend()

    return fig, lines_uncal, lines_cal

def plot_snapshots(lines, snapdata_list, nsamples):
    """
    Plot snapshot data in figure.
    :param lines: matplotlib lines where to set the data.
    :param snapdata_list: list of data to plot.
    :param nsamples: number of samples og the snapshot to plot.
    """
    for line, snapdata in zip(lines, snapdata_list):
        line.set_data(range(nsamples), snapdata[:nsamples])

def plot_spectra(lines, snapdata_list, bandwidth, dBFS):
    """
    Plot spectra data in figure.
    :param lines: matplotlib lines where to set the data.
    :param snapdata_list: list of data to plot.
    :param bandwidth: spectral data bandwidth.
    :param dBFS: shift constant to convert data to dBFS.
    """
    nchannels = len(snapdata_list[0])/2
    freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)
    for line, snapdata in zip(lines, snapdata_list):
       # compute the fft of snapshot data
       spec = np.square(np.abs(np.fft.rfft(snapdata)[:-1]))
       spec = cd.scale_and_dBFS_specdata(spec, nchannels, dBFS)
       line.set_data(freqs, spec)

def perform_mmcm_calibration(roach, zdok, snapnames):
    """
    Perform MMCM calibration using Primiani's adc5g package.
    :param roach: FpgaClient object to communicate with ROACH.
    :param zdok: ZDOK port number of the ADC to calibrate (0 or 1).
    :param snapnames: list of snapshot blocks used for the calibration.
        Must have either 1 or 2 snapshot names.
    """
    adc5g.set_test_mode(roach, zdok)
    adc5g.sync_adc(roach)

    print("Performing ADC5G MMCM calibration, ZDOK" + str(zdok) + "...")
    opt, gliches = adc5g.calibrate_mmcm_phase(roach, zdok, snapnames)
    adc5g.unset_test_mode(roach, zdok)
    print("done")

def compress_data(datadir):
    """
    Compress the data from the datadir directory into a .tar.gz
    file and delete the original directory.
    """
    tar = tarfile.open(datadir + ".tar.gz", "w:gz")
    for datafile in os.listdir(datadir):
        tar.add(datadir + '/' + datafile, datafile)
    tar.close()
    shutil.rmtree(datadir)

def uncompress_data(datadir):
    """
    Uncompress .tar.gz data from the datadir directory.
    """
    os.mkdir(datadir)
    tar = tarfile.open(datadir + ".tar.gz")
    tar.extractall(datadir)
    tar.close()

