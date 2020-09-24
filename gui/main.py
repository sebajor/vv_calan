from Tkinter import *
import vv_calan
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from matplotlib.figure import Figure
#import ipdb
import time, threading 
import tkMessageBox

""" idea----> the spectrum and corr other plots are shown in a new window

 Buttons        |
 and typical    |   plot of the measurement 
 stuffs         |
                |
                |
                |
----------------|-------------
Optional        |   text output of the optional 
stuffs          |   stuffs
                |
"""


class MainWindow:

    def __init__(self, root):
        self.root = root
        input_frame = Frame(root, padx=10, pady=10)
        input_frame.grid(row=0, column=0)
        
        bof_label = Label(input_frame, text="bof path:")
        bof_label.grid(row=0, column=0)
        self.bof_entry = Entry(input_frame, width=15)
        self.bof_entry.grid(row=0,column=1)
        self.bof_entry.insert(0, "vv_casper.bof")
        
        roach_ip_lbl = Label(input_frame, text="Roach IP:", pady=10)
        roach_ip_lbl.grid(row=1, column=0)
        self.roach_ip = Entry(input_frame, width=15)
        self.roach_ip.insert(0, "192.168.0.40")
        self.roach_ip.grid(row=1,column=1, pady=10)
        
        synth_clk_lbl = Label(input_frame, text="Valon \n Freq[MHz]:", pady=5)
        synth_clk_lbl.grid(row=2, column=0)
        self.synth_clk = Entry(input_frame, width=15)
        self.synth_clk.insert(0, "1080")
        self.synth_clk.grid(row=2, column=1) 
        
        intg_lbl = Label(input_frame, text="Integration \ntime[ms]:", pady=10)
        intg_lbl.grid(row=3, column=0)
        self.intg_time = Entry(input_frame, width=15)
        self.intg_time.insert(0, "1.2")
        self.intg_time.grid(row=3,column=1)
        
        chan_freq_lbl = Label(input_frame, text="Frequency \n to save")
        chan_freq_lbl.grid(row=4, column=0)
        self.chan_freq = Entry(input_frame, width=15)
        self.chan_freq.grid(row=4, column=1) 
        self.chan_freq.insert(0, "50")
    
        time_lbl = Label(input_frame, text="Time to save\n [min]")
        time_lbl.grid(row=5, column=0)
        self.time2save = Entry(input_frame, width=15)
        self.time2save.grid(row=5, column=1)
        self.time2save.insert(0, "30")

        self.init_roach = Button(input_frame, text="Program vector \n voltmeter", padx=10,
                                pady=10, command=self.program_roach, width=10, height=1)

        self.init_roach.grid(row=6, column=0)

        self.init_irig = Button(input_frame, text="Calibrate IRIG", padx=10, pady=10,
                                command=self.calibrate_irig, width=10, height=1)
        self.init_irig.grid(row=6, column=1,columnspan=2)
        
        
        #Measure

        self.meas = Button(input_frame, text="Start\n measure", 
                            command=self.start_meas, pady=5, width=10)
        self.meas.grid(row=7, column=0)
        
        self.end_meas = Button(input_frame, text="End\n measure", 
                            command=self.end_meas, pady=5, width=10)
        self.end_meas.grid(row=7, column=1)

        ##plot frame
        plot_frame = Frame(root, padx=10, pady=8)
        plot_frame.grid(row=1, column=0)
        plot_lbl = Label(plot_frame, text="Plots", font="Helvetica")
        plot_lbl.grid(row=0, column=0)

        
        self.full_spect = BooleanVar()
        self.full_spect.set(True)
        self.full_phase = BooleanVar()
        self.full_phase.set(True)
        self.chann_vars = BooleanVar()

        spect_plot = Checkbutton(plot_frame, text="Spect", variable=self.full_spect)
        phase_plot = Checkbutton(plot_frame, text="Phase", variable=self.full_phase)
        chann_plot = Checkbutton(plot_frame, text="Channel", variable=self.chann_vars)

        spect_plot.grid(row=1, column=0)
        phase_plot.grid(row=1, column=1)
        chann_plot.grid(row=2, column=0)

        ###
        
        beg_bw_lbl = Label(plot_frame, text="start plot bw:").grid(row=3, column=0)
        self.beg_bw = Entry(plot_frame, width=5)
        self.beg_bw.insert(0, "0")
        self.beg_bw.grid(row=3, column=1, padx=1)
        end_bw_lbl = Label(plot_frame, text="end plot bw:").grid(row=4, column=0)
        self.end_bw = Entry(plot_frame, width=5)
        self.end_bw.insert(0, "67.5")
        self.end_bw.grid(row=4, column=1, padx=1)
        
        ### 
        
        self.snap_btn = Button(plot_frame, text="ADC \nsnapshot",
                                command=self.snap, height=3)
        self.snap_btn.grid(row=5, column=0,pady=3)
        
        self.plotting = Button(plot_frame, text="Generate \n plots",
                                command=self.plot_data,
                                height=3)
        self.plotting.grid(row=5, column=1, pady=3)

        
        


        ###Optional stuffs
        option_frame = Frame(root, padx=5, pady=20)
        option_frame.grid(row=2, column=0)
        self.valon_check = Button(option_frame, text="Check \nclocks", 
                                  pady=10, command=self.check_freq, width=9)
        self.valon_check.grid(row=0, column=0) 

        self.roach_clk_check = Button(option_frame, text="Get \nRoach time",
                                 pady=10, command=self.roach_time, width=9) 
        self.roach_clk_check.grid(row=0, column=1)
   
        self.cal_adc = Button(option_frame, text='ADC \ncalibration',
                                pady=10, command=self.adc_cal, width=9)
        self.cal_adc.grid(row=1,column=0)
       
        self.set_valon = Button(option_frame, text='Set \nValon',
                                pady=10, command=self.set_valon, width=9)
        self.set_valon.grid(row=1,column=1)
        
        check_ppc_status = Button(option_frame, text="Check \nPPC",
                                pady=10,command=self.check_ppc, width=9 )
        check_ppc_status.grid(row=1,column=2)

        #cmd response
        cmd_space = Frame(root, padx=40, pady=10)#, bg="white"#, width=950, height=100)
        cmd_space.place(x=350,y=570)##grid(row=0, column=3)
        #self.cmd_val = StringVar()
        #self.cmd_val.set("cmd repsonse:\t asd")
        self.cmd_resp = Label(cmd_space, text="cmd response:", justify=RIGHT)
                              #bg="black", fg="white")
        self.cmd_resp.grid(row=0, column=0)
    

        #plot space
        self.plot_space = Frame(root, padx=40, pady=10, bg="grey", width=950, height=520)
        self.plot_space.place(x=300,y=20)##grid(row=0, column=3)
        #self.f = Figure()
         
        

    """#Example of one plot 
    ###plot canvas

        self.plot_space = Frame(root, padx=40, pady=10, bg="grey", width=1000, height=550)
        self.plot_space.place(x=300,y=20)##grid(row=0, column=3)
        self.f = Figure()
        self.axis = self.f.add_subplot(111)
        t = np.arange(0,3,0.01)
        s = np.sin(2*np.pi*t)
        self.axis.plot(t,s)

        self.canvas = FigureCanvasTkAgg(self.f, master=self.plot_space)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_space)
    """
        


    
    def program_roach(self):
        ##TODO: upload bof and init vector voltmeter
        ##if the system was programed make a pop up to warn
        ## that if is reprogrammed you lose your actual measure

        ##PROBLEM:WHEN THE IP IS WRONG THE SYSTEM HANGS!!!!!
        bof_path =  self.bof_entry.get()
        roach_ip = self.roach_ip.get()
        valon_freq = int(self.synth_clk.get())
        int_time = float(self.intg_time.get())*10**-3
        self.roach = vv_calan.vv_calan(roach_ip, bof_path, valon_freq)
        print(int_time)
        #ipdb.set_trace()
        try:
            time.sleep(1)
            self.roach.upload_bof()
            print("upload bof")
            time.sleep(1)
            self.roach.init_vv(integ_time=int_time)
            print("init vv")
            time.sleep(0.5)
            fpga_clk = self.roach.get_aprox_clk()
            n_acc = self.roach.n_acc
            chann_period = 2.**14/(1.*valon_freq/8*10**6)
            integ_time = chann_period*n_acc*10**3
            self.cmd_resp.config(text="cmd response:\t Succed! \n \t\tFpga running at ~"+str(fpga_clk)+
                                "\n \t\taccumulation set to "+str(n_acc)+" --->"+
                                 str(integ_time)+"ms", justify=LEFT)
        except:
            self.cmd_resp.config(text="cmd response:\t Error! Check your inputs", justify=LEFT)


        return 
    
    def calibrate_irig(self):
        """ I modify the code a little... test if it works in Calan!
        """
        try:
            self.roach.calibrate_timestamp()
            timestamp = self.roach.get_hour()
            unlock = self.get_unlock()
            self.cmd_resp.config(text="cmd response:\t Calibration finish\n\t\t"+
                                 "timestamp:"+str(timestamp)+"\n\t\t unlocked:"+str(unlock),
                                 justify=LEFT)
        except:
            self.cmd_resp.config(text="cmd response:\t Calibration failed...")
        return

    
    def snap(self):
        ##possible TODO: make it appear in the main screen 
        try:
            self.roach.adc_snapshot()
        except:
            self.cmd_resp.config(text="cmd response:\t ERROR! did you intialize the system?...")
        return

    def plot_data(self):
        ##TODO
        #ipdb.set_trace()
        spect = self.full_spect.get()
        phase = self.full_phase.get()
        chann = self.chann_vars.get()
        chann2save = self.roach.get_index(float(self.chan_freq.get()))
        beg_bw = float(self.beg_bw.get())
        end_bw = float(self.end_bw.get())
        plot_list = []
        if(spect):
            plot_list.append('spect0')
            plot_list.append('spect1')
        if(phase):
            plot_list.append('phase')
        if(chann):
            plot_list.append('chann_values')
        if(len(plot_list)==0):
                self.cmd_resp.config(text="cmd response:\t You hadn't mark any plot..")
                return
        else:
            try:
                if(not hasattr(self.roach, 'plotter')):
                    self.roach.create_plot()

                #self.roach.generate_plot(plots=plot_list, chann=chann2save, freq=[beg_bw, end_bw])
                threading.Thread(target=self.roach.generate_plot(plots=plot_list, chann=chann2save, freq=[beg_bw, end_bw])).start()
                return    
            except:
                self.cmd_resp.config(text="cmd response:\t Error :(")
                return
                

    def start_meas(self):
        time2save = float(self.time2save.get())
        cmd_text = "cmd response: \t uploading the codes to the ppc..."
        self.cmd_resp.config(text=cmd_text, justify=LEFT)
        try:
            self.roach.ppc_upload_code()
            cmd_text = cmd_text+'done\n\t\t initializing measurement...'
            self.cmd_resp.config(text=cmd_text, justify=LEFT)
            self.pid = self.roach.ppc_meas()
            cmd_text = cmd_text+'done\t Process runnign with PID:'+str(self.pid)
            self.cmd_resp.config(text=cmd_text, justify=LEFT)
        except:
            cmd_text = cmd_text+"Fail! \n Error :(" 
        return 

    def end_meas(self):
        try:
            #ipdb.set_trace()
            check = self.roach.ppc_check_status()
            if(check):
                #popup warning that you are going to kill the measure before it finish
                r = tkMessageBox.askyesno("kill pid confirmation","You are going to kill the measurement process"+
                            "\n Are you sure?")
                if(r):
                    self.roach.ppc_finish_meas()
                    check = self.roach.ppc_check_status()
                    if(check):
                        aux = 'running'
                    else:
                        aux = 'killed'
                    self.cmd_resp.config(text="cmd response: \t PID state: "+aux, justify=LEFT)
                else:
                    return
            else:
                self.cmd_resp.config(text="cmd response: \tProcess already finished", justify=LEFT)
        except:
            self.cmd_resp.config(text='cmd response: \tError!', justify=LEFT)
        return

    def roach_time(self):
        ##TODO
        timestamp = self.roach.get_hour()
        unlock = self.roach.get_unlock()                                          
        self.cmd_resp.config(text="cmd response: \t timestamp:"+str(timestamp)+"\n\t\t unlocked:"+str(unlock),
                                 justify=LEFT)
        return

    def adc_cal(self):
        ##TODO
        return

    def check_freq(self):
        ##TODO: check valon + roach freq
        approx_clk = self.roach.get_aprox_clk()
        derived_clk = self.roach.get_fpga_clock()
        self.cmd_resp.config(text="cmd response: \t approximated fpga clock:\t"+str(approx_clk)+
                                "\t--->Valon:"+str(approx_clk*8)+"\n\t\t user-entered clock:\t"
                                +str(derived_clk)+"\t\t--->Valon:"+str(derived_clk*8),
                                    justify=LEFT)

        return
    def set_valon(self):
        ##TODO
        return 

    def check_ppc(self):
        check = self.roach.ppc_check_status()
        if(check):
            self.cmd_resp.config(text="cmd response: \t Process still running",
                                 justify=LEFT) 
        else:
            self.cmd_resp.config(text="cmd response: \t Process stopped",
                                  justify=LEFT) 
        return


if __name__ == '__main__':
    root = Tk()
    root.title("Roach")
    asd= MainWindow(root)
    root.mainloop()
