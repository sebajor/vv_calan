import corr,time,os, telnetlib
import calandigital as calan
from plot_snapshot import snapshot
from powerpc import PPC_upload_code, PPC_start_measure,PPC_download_data, PPC_kill_process, PPC_check_status
from parse_raw import parse_raw
from plots import plot_data
from get_data import get_spect0, get_spect1, get_phase, init_chann_data, get_chann_data
import numpy as np
import pkg_resources
from calibrate_adcs import calibrate_adcs_visa
import valon_config


class vv_calan(object):
    def __init__(self, roachIP, bof_path, valon_freq, upload=0):
        """ Class constructor
            valon freq is the actual frequency of the valon,
            not the sampling frequency.
            ##Remember the sampling frequency is the double
            of the valon frequency
        """
        self.path = pkg_resources.resource_filename('vv_calan', 'ppc_save')
        self.IP = roachIP
        self.bof = bof_path
        self.valon_freq = valon_freq
        self.fpga_clk = valon_freq/8.
        self.bw = self.fpga_clk/2   #this is the bw after the decimation
        
        #self.fpga = corr.katcp_wrapper.FpgaClient(self.IP)
        self.fft_size = 2**14
        self.channels = 2**13
        self.n_acc = 10
        if(upload):
            self.fpga = calan.initialize_roach(self.IP, boffile=self.bof, upload=0) 
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(roachIP)


    def upload_bof(self):
        """Upload the bof file to the ROACH
        """
        self.fpga = calan.initialize_roach(self.IP, boffile=self.bof, upload=1) 
        #self.fpga.upload_program_bof(self.bof, 3000)
        time.sleep(1)

###
###     VECTOR VOLTMETER INITIALIZATION CODES:
###             BEFORE ANY TYPE OF MEASUREMENT YOU MUST
###             INITIALIZE THE SYSTEM AND SET THE 
###             INTEGRATION TIME.
###
###             
###


    def set_integ_time(self, integ_time=1.2*10**-3):
        """Set integration time 
           integ_time = imtegration time in seconds
        """    
        chann_period = 2.**14/(self.fpga_clk*10**6) #
        self.n_acc = int(integ_time/chann_period)+1
        if(self.n_acc>2**14-2):
            print("The accumulation could overflow, carefull look at the spectrum..") 
        self.fpga.write_int('acc_len',self.n_acc)
        self.fpga.write_int('cnt_rst',1)
        self.fpga.write_int('cnt_rst',0)
        print("integration time set to: %.4f [ms]"%(self.n_acc*chann_period*10**3))


    def init_vv(self, integ_time=1.2*10**-3):
        """initialize the vector voltmeter registers
        """
        self.fpga.write_int('cnt_rst',1)
        self.set_integ_time(integ_time)
        self.fpga.write_int('cnt_rst',0)


###
###     IRIG TIMESTAMP INITIALIZATION CODES:
###             IF YOU WANT TO USE THE TIMESTAMP YOU MUST
###             INITIALIZE THE SYSTEM AND THEN CALIBRATE
###             IT USING AS INPUT A IRIG MASTER CLOCK
###             YOU COULD ACCESS TO CHECK THE ACTUAL TIME,
###             YOU COULD READ A REGISTER TO CHECK IF
###             THE TIME DRIFT IS LESS THAN A CERTAIN
###             THRESHOLD.
###


    def init_timestamp(self, unlock_error=10**-4):
        """initialize the timestamp model
            unlock_error = the varition in seconds to rise an
            unlock flag
        """
        fpga_clk = self.fpga_clk*10**6
        sec_parameter = 1.05
        irig_0 = int(0.2*fpga_clk/100*sec_parameter)
        irig_1 = int(0.5*fpga_clk/100*sec_parameter)
        irig_pos_id = int(0.8*fpga_clk/100*sec_parameter)

        print('writing timestamp variables.....')
        self.fpga.write_int('IRIG_control', 0b001)  #rst the fsm
        
        #enable voltage translation, 
        self.fpga.write_int('IRIG_voltage_oe',2)

        #those are the durations of every symbol in IRIG
        self.fpga.write_int('IRIG_irig_pos_id', irig_pos_id)
        self.fpga.write_int('IRIG_irig_1', irig_1)
        self.fpga.write_int('IRIG_irig_0', irig_0)

        #settings for the debouncer fsm
        self.fpga.write_int('IRIG_waiting_in_vain', 20) #cycles that the gpio values may vary until sets to one


        #set upper and lower limit of seconds that the timestamp
        #could vary to rise the flag of unlocking
        self.fpga.write_int('IRIG_frec_uplim', int(self.fpga_clk*10**6*(1+unlock_error)))   
        self.fpga.write_int('IRIG_frec_downlim', int(self.fpga_clk*10**6*(1-unlock_error))) 

        ##with the previous registers set up, we obtain the time from the master clock
        self.calibrate_timestamp()



    def calibrate_timestamp(self):
        """Get the time from the master clock
         This function enable obtain the time from the master clock
        """
        #reset the fsm to a known state
        self.fpga.write_int('IRIG_control', 0b101)
        time.sleep(1)
        #start the calibration
        self.fpga.write_int('IRIG_control', 0b010)

        #wait until the first frame is detected and received
        print('waiting for the master clock data...')
        time.sleep(3)
        for i in range(5):
            time.sleep(1)
            aux = self.fpga.read_int('IRIG_terminate')
            if(aux == 1):
                break

        if(i==4):
            print('There might be a problem..its everything connected?')
            ans = raw_input('Do you want to try the calibration again?(y/n)')
            if(ans=='y' or ans=='yes'):
                self.calibrate_timestamp()
            else:
                return
        else:
            #The first second is always over the upper lim, and the second its always below the lower lim because
                # the fraction counter initialize only when the calibration is over. 
                #From the third second the system is stable, so we rest the unlock flag.
            time.sleep(2)
            self.fpga.write_int('IRIG_control',0b110)
            self.fpga.write_int('IRIG_control',0b010)

            print('Timestamp calibration finished :D')




    def get_hour(self):
        """Translate the time from seconds of a year
        to day/hour/minutes/seconds
        """
        time_data = self.fpga.read_int('secs')
        secs = time_data&63
        mins = (time_data&(63<<6))>>6
        hour = (time_data&(31<<12))>>12
        day = (time_data&((2**9-1)<<17))>>17
        out = str(day)+'day'+str(hour)+':'+str(mins)+':'+str(secs)
        print(out)
        return [secs,mins,hour,day]


    def get_unlock(self):
        """ return 1 if the timestamp is unlocked
            return 0 if the timestamp is locked
        """
        out = self.fpga.read_int('unlock')
        return out




### 
###      PLOTS: YOU COULD LOOK AT THE INPUT IN THE ADCS
###             LOOK THE SPECTRUM, CORRELATION AND RELATIVE
###             PHASE OF THE INPUTS        
###

    def adc_snapshot(self):
        """Plot animation of the ADC snapshot
        """
        snapshot(self.fpga)

    def create_plot(self):
        self.plotter = plot_data(self.fpga)

    def generate_plot(self, plots=['spect0','spect1'],chann=6068, freq=[0,67.5],manual_bw=0,bw=[0,67.5]):
        """
            Plots an animation of the real time value (at the
            network speed).
            
            plot_type is a list which may contain the following
            options:
        
            -spect0: gives the spectrum of the ADC0
            -spect1: gives the spectrum of the ADC1
            -correlation: gives the real part and imaginary part
            of the correlation of the whole range of channels
            -phase: gives the relative phase between the 
            ADC0 and ADC1 for whole range of FFT channels.
            -chann_values: gives the magnitud of a given channel
            in the ADC0 and ADC1, also gives the phase measured 
            between the inputs.
        
        """
        if(manual_bw):
            self.plotter.plotter(plots, chann=chann, freq=freq, bw=bw, acc_len=self.n_acc)        
        else:
            self.plotter.plotter(plots,chann=chann, freq=freq,bw=[0,self.bw], acc_len=self.n_acc)

###
###    POWERPC CODES: YOU MUST UPLOAD THE CODES TO THE 
###                   MICRO WHEN YOU WANT TO MAKE A MEASUREMENT
###                   THEN YOU COULD INITIALIZE THE MEASURE
###                   FINALLY YOU COULD KILL THE PROCESS  
###                   AND DOWNLOAD THE COLLECTED DATA
###                   WE PROVIDE A FUNCTION TO PARSE THE DATA
###                   AND GIVE IT IN HDF5 FORMAT
###


    def ppc_upload_code(self, file_path='ppc_save', sleep_time=0.5):
        """Upload the required files to the ppc in the ROACH
        We connect through telnet to the 
        """
        if(file_path!='ppc_save'):
            PPC_upload_code(self.IP, (file_path), sleep_time=sleep_time)
        else:
            PPC_upload_code(self.IP, self.path, sleep_time=sleep_time)


    def ppc_meas(self, chann=6068 ,duration=30, sleep_time=0.5):
        """Measure and save the data in the PowerPC in the roach
           duration=time of the complete measure, in minutes 
        """
        ###TODO: check if some registers must be cleaned before...
        self.fpga.write_int('addr2catch', chann) #select the channel to save in the ppc
        bram_addr = 8192.
        bram_period = self.fft_size*bram_addr*self.n_acc/(self.fpga_clk*10**6)*2 #we have two banks
        self.__read_cycles__ = int(duration*60./bram_period)
        self.__pid__ = PPC_start_measure(self.IP,self.__read_cycles__, sleep_time=sleep_time)
        print("PID of the process: "+str(self.__pid__))

    def ppc_check_status(self, sleep_time=0.5):
        stat = PPC_check_status(self.IP, sleep_time=sleep_time)        
        return stat

    def ppc_download_data(self, pc_IP, sleep_time=2):
        """Download the saved data to a computer
        """
        PPC_download_data(self.IP, pc_IP)
        time.sleep(sleep_time)


    def ppc_finish_meas(self, sleep_time=0.5):
        """Finish the measurement before measure duration has 
           elapsed
        """
        PPC_kill_process(self.IP, self.__pid__, sleep_time=sleep_time)



    def parse_raw_data(self, filename='raw_data', out_name=None):
        """
        Parse the raw data after downloading the data from the 
        PowerPC and save it in hdf5 format.
        """
        #print('This method runs by default using the measurent duration as input to calculate the size of the file')
        #print('If you had killed the process before it finished you could use the number of readings variable to change it.')
        #first get the size of the file and get the 
        chunk = 5*8192*8
        file_size = os.path.getsize(filename)
        n_reading = file_size/chunk
        parse_raw(filename, n_reading, out_name=out_name)
        #if(n_reading==None):
        #    parse_raw(filename, self.__read_cycles__*2, out_name=out_name)
        #else:
        #    parse_raw(filename, n_reading,out_name=out_name)



###
###     CALIBTRATION CODES: BEFORE ANY SERIOUS MEASUREMENT YOU
###                         MUST MAKE CALIBRATION TO THE ADCS
###                         REFEAR TO THE DOCUMENT ATACHED IN
###                         THE GITHUB PAGE.
    """     ##old way to calibrate..
    def calibration(self, load=0, man_gen=0, ip_gen='192.168.1.33', filename='cal'):
        This function makes the calibration of the ROACH more 
        understandable; you have to had installed the package 
        calandigital (https://github.com/FrancoCalan/calandigital)
        if you only want to make mcmm set load at 1
        if you want to manually set the generator set man_gen=1
        ip_gen = generator IP, to use in this mode the generator must
                 support visa commands
        filename = if load=1 the load dir, if load=0 the saving dir


            -Sidenote: a common failure is to set bad the bw and it throws
            an error of representation

        parameter = "calibrate_adc5g.py"
        parameter += " -i "+str(self.IP)
        if(man_gen==0):
            parameter += " -g "+str(ip_gen)
            parameter += " -gf "+str(10)
            parameter += " -gp "+str(-3)
        parameter += " -psn -psp"
        parameter += " -bw "+str(self.valon_freq)
        parameter += " -s0 adcsnap0"
        parameter += " -s1 adcsnap1"
        parameter += " -ns 1000"
        if(load==0):
            parameter += " -dm -di -do"
            parameter += " -cd "+str(filename)
        if(load==1):
            parameter += " -dm -li -lo"
            parameter += " -ld "+str(filename)
        print(parameter)    
        os.system(parameter)
        """
    def calibrate_adcs(self,gen_ip, do_ogp=0, do_inl=0,gen_freq=10,gen_pow=-3,load=0,load_dir='',cal_dir='adc5gcal',manual=0):
        calibrate_adcs_visa(self.IP, gen_ip,self.valon_freq,do_ogp=do_ogp, do_inl=do_inl,
                gen_freq=gen_freq, gen_pow=gen_pow, load=load, load_dir=load_dir, 
                cal_dir=cal_dir, manual=manual)




        ###
###     CHANGE THE VALON FREQUENCY: TO USE THE CODES YOU MUST CONNECT
###                                 TO THE BACK OF THE ROACH WITH A 
###                                 MICRO-USB CONNECTOR.
###                                 CHECK ALSO WICH TTY IS CREATED
###                                 CHANGING THIS VALUE AFECT THE FPGA 
###                                 CLOCK TOO.
###
    
    #def get_valon_status(self, port=1):
        """Prints the actual configuration of the valon
        """
        """
        parameter = "python adc_clock.py"
        if(port):
            parameter += ' -s B'
        else:
            parameter += ' -s A'
        os.system(parameter)

    def set_valon_ref(self, ref='i', port=1):
        parameter = "python adc_clock.py"
        if(port):
            parameter += ' -s B'
        if(not port):
            parametr += ' -s A'
        if(ref=='i'):
            parameter +=' -i'
        if(ref=='e'):
            parameter +=' -e'
        os.system(parameter)
"""
    def get_valon_status(self, port='/dev/ttyUSB0', synth='B'):
        s, synth_num = valon_config.get_valon_status(port=port, synth=synth)
        s.conn.close()
    
    #def set_valon_freq(self, new_freq, port=1):
        """
        To use this function is necessary to be connected 
        to the USB port of the valon
        new freq: Its the sampling frequency of the ADC's
        port: which port we are programming, 0 means A and 1 means B
        ##The actual sampling frequency is the double of new_freq
        beacause the ADC take a sample at the rising and falling edge

        After changing the clock you should reset the vector voltmeter
        register and re-calibrate the timestamp.

        #If you have some problem change the tty in the adc_clock script
        """
    """
        parameter = "python adc_clock.py -f" + str(int(new_freq/2))
        if(port):
            parameter += ' -s B'
            os.system(parameter)
            self.valon_freq = new_freq
            self.fpga_clk = self.valon_freq/8
            self.bw = self.fpga_clk/2
        else:
            parameter += ' -s A'
            os.system(parameter)
"""
    def set_valon_freq(self, new_freq, port='/dev/ttyUSB0', synth='B', res=10.0):
        valon_config.set_valon_freq(new_freq=new_freq, port=port, synth=synth, res=res)
        self.valon_freq = new_freq
        self.fpga_clk = self.valon_freq/8.
        self.bw = self.fpga_clk/2   #this is the bw after the decimation
        

    def set_valon_ref(self, ref='i', port='/dev/ttyUSB0', synth='B'):
        valon_config.set_valon_ref(ref=ref,port=port, synth=synth)


    def synchronization(self):
        ##TODO...
        return    

    def get_aprox_clk(self):
        """Gives an estimation measured inside of the FPGA
            of the fpga clock value. It is not exact as look at the 
            valon frequency directly.
        """
        clk_aprox = self.fpga.est_brd_clk()
        print(clk_aprox)
        return clk_aprox

###
###     SIMPLE GETTERS AND SETTERS
###
###

    def get_sampling_freq(self):
        """Returns the sampling frequency at the ADC using the 
           user provided information. You could use the approx_clk
           to stimate the current frequency.
        """
        return self.valon_freq*2


    def get_fpga_clock(self):
        """Return the fpga clock, this is twice of
            the usefull bandwidth.
        """
        return self.fpga_clk


    def get_adc0_spect(self):
        out = get_spect0(self.fpga)
        return out

    def get_adc1_spect(self):
        out = get_spect1(self.fpga)
        return out

    def get_rel_phase(self):
        out = get_phase(self.fpga)
        return out

    def get_index(self, freq):
        """given a input frequency returns the
           nearest dft point.
           freq: frequency in MHz in the range (0-bw)
        """
        freqs = np.linspace(0, self.bw, self.channels, endpoint=False)
        ind = np.argmin(np.abs(freq-freqs))
        return ind

#THE FUNCTIONS DOWN THIS LINE ARE USED IN THE
#MAP CREATION.. THEY DONT GET ALONG WITH THE
#OPTION plots=['chan_values'] IN THE generate_plot
#BECAUSE IT CHANGES THE NUMBER OF POINTS TAKEN.
#SO TAKE CARE OF THAT

    def init_chann_aqc(self, chann=6068, n_samp=1, continuous=1):
        """Initialize the one channel acquisition.
           channel: dft channel you want to look at
           n_samp: the number of samples that you want to store in bram
                   support values in the range (1-8192)
           cont: if you want to acquire continously data in the bram using
                 a free running  counter or you want to store n_samples
                 and keep it until you read it.
                 If you select the second option you must be aware that
                 is your job reset the counter and enable the storing again
                 after you read the data.(use the function rst_freeze_cntr
                 after the read)
        """
        init_chann_data(self.fpga, chann=chann, n_samp=n_samp, continous=continuous)


    def get_chann_data(self, n_samp=1):
        """Get the data (power in ADC0, ADC1, correlation)
           of one given channel, before using it you must 
           have initialize with init_chann_aqc.

           n_samp: must be the same value used in the
                   initialization function

            ###obs: the powers are not in dB...

        """
        [adc0,adc1, corr_re, corr_im] = get_chann_data(self.fpga, n_samp)
        return [adc0, adc1, corr_re, corr_im]


    def gen_pulse_out(self, pulse_width=50):
        """pulse width: width of the pulse in ms
        """
        self.fpga.write_int('pulse_out',0)  #rst the machine
        self.fpga.write_int('pulse_width', int(pulse_width*self.fpga_clk*10**3))
        time.sleep(0.1)
        self.fpga.write_int('pulse_out',1)
        time.sleep(0.1)
        time_data = self.fpga.read_int('pulse_sec')
        #sec = self.get_hour(sec)
        secs = time_data&63
        mins = (time_data&(63<<6))>>6
        hour = (time_data&(31<<12))>>12
        day = (time_data&((2**9-1)<<17))>>17
        out = [secs, mins,hour,day]
        sub_sec = self.fpga.read_int('pulse_subsec')
        return [out, sub_sec]
        

    def timeroach(self, time_data, subsec, fpga_clk=135*10**6):
        secs = time_data&63
        mins = (time_data&(63<<6))>>6
        hour = (time_data&(31<<12))>>12
        day = (time_data&((2**9-1)<<17))>>17
        sub = subsec/float(fpga_clk)
        out = [sub,secs, mins,hour,day]
        return out


    def reset_freeze_cntr(self):
        #TODO
        return


