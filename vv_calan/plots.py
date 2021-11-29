import matplotlib.pyplot as plt
import numpy as np
import time 
import matplotlib.animation as animation
from get_data import *



class plot_data():
    def __init__(self, fpga):
        """class constructor
        """
        self.fpga = fpga
        fpga.write_int('cnt_rst',0)

    def plotter(self, plots, chann=6068, freq=[0,67.5], bw=[0,67.5], n_points=8192, acc_len=10):
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
        self.acc_len = float(acc_len)
        self.plots = plots
        self.chann = chann
        self.freq = freq
        self.n_points = n_points #n of points to use in the chann_values

        self.fft_freq = np.linspace(bw[0], bw[1], 2**13, endpoint=False)
        
        self.anim = []

        if('chann_values' in self.plots):
            ##Create the plot for the channel values in a 
            ##different window
            self.plots.remove('chann_values')
            init_chann_data(self.fpga,self.chann, n_samp=self.n_points) #initialize the acquisition logic
            self.plot_chann()
    
        if('correlation' in self.plots):
            self.plots.remove('correlation')
            self.plots.append('corr_re')
            self.plots.append('corr_im')

    
        self.plot_info = {  'spect0':['Spectrum ADC0', '[dBm]', '[MHz]',(-110, 0), (self.freq)],
                            'spect1':['Spectrum ADC1', '[dBm]', '[MHz]', (-110, 0), (self.freq)],
                            'corr_re':['Real Correlation', '[dB]', '[MHz]', (15, 180), (self.freq)],
                            'corr_im':['Imaginary Correlation', '[dB]', '[MHz]', (15,180), (self.freq)],
                            'phase':['Relative Phase', 'deg', '[MHz]', (-180, 180), (self.freq)]}
                
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22', 5:'23'}
        self.create_plots()
        anim = animation.FuncAnimation(self.fig_plots, self.anim_plots, blit=True)
        plt.show()                    




    def create_plots(self):
        self.fig_plots = plt.figure()
        axis = []
        self.data = []
        for i in range(len(self.plots)):
            info = self.plot_info[self.plots[i]]
            ax = self.fig_plots.add_subplot(self.plot_map[len(self.plots)]+str(i))
            ax.grid()
            ax.set_title(info[0])
            ax.set_ylabel(info[1])
            ax.set_xlabel(info[2])
            ax.set_ylim(info[3])
            ax.set_xlim(info[4])

            axis.append(ax)
            ax_data, = ax.plot([],[],lw=2)
            self.data.append(ax_data)

            
        
    def get_data(self):
        output = []
        for i in range(len(self.plots)):
            if(self.plots[i] == 'phase'):
                data = get_phase(self.fpga)
                output.append(data)
                continue
            if(self.plots[i] == 'spect0'):
                data = get_spect0(self.fpga, self.acc_len)
                data = data-138.3
                output.append(data)
                continue
            if(self.plots[i] == 'spect1'):
                data = get_spect1(self.fpga, self.acc_len)
                data = data-138.3
                output.append(data)
                continue
            if(self.plots[i] == 'corr_re'):
                data = get_corr_re(self.fpga)
                output.append(data)
                continue
            if(self.plots[i] == 'corr_im'):
                data = get_corr_im(self.fpga)
                output.append(data)
                continue
            else:
                raise Exception('One value in the plot list is not suported :(')
            
        return output


    def anim_plots(self, i):
        data = self.get_data()
        for i in range(len(self.plots)):
            self.data[i].set_data(self.fft_freq, data[i])
        return self.data
        
            
    




    def plot_chann(self):
        self.create_chann_plot()
        anim_chann= animation.FuncAnimation(self.fig_chann, self.anim_chann, blit=True)
        self.anim.append(anim_chann)        


    def create_chann_plot(self):
        self.fig_chann = plt.figure()
        ax1 = self.fig_chann.add_subplot(211)
        ax2 = self.fig_chann.add_subplot(223)
        ax3 = self.fig_chann.add_subplot(224)
        
        ax1.set_title('Relative phase')
        ax1.set_ylabel('['+u'\xb0'+']')
        ax1.set_xlabel('Samples')
        ax1.set_ylim(-180, 180)        
        ax1.set_xlim(0, self.n_points)
        
        ax2.set_title('ADC0 power')
        ax2.set_ylabel('[dB]')
        ax2.set_xlabel('Samples')
        ax2.set_ylim(-110, 0)
        ax2.set_xlim(0, self.n_points)
        
        ax3.set_title('ADC1 power')
        ax3.set_ylabel('[dB]')
        ax3.set_xlabel('Samples')
        ax3.set_ylim(-110, 0)
        ax3.set_xlim(0, self.n_points)

        ax1.grid()
        ax2.grid()
        ax3.grid()
        
        dat1, = ax1.plot([],[], lw=2)
        dat2, = ax2.plot([],[], lw=2)
        dat3, = ax3.plot([],[], lw=2)

        self.data_chann = [dat1, dat2,dat3]

        
    def anim_chann(self, i):
        [pow0, pow1, re, im] =  get_chann_data(self.fpga, self.n_points)
        pow0 = pow0/float(self.acc_len)
        pow1 = pow1/float(self.acc_len)
        powA = 10*np.log10(pow0+1)-138.3  ##to match dbm
        powB = 10*np.log10(pow1+1)-138.3
        ang = np.rad2deg(np.arctan2(im,re))
        
        self.data_chann[0].set_data(np.arange(self.n_points), ang)
        self.data_chann[1].set_data(np.arange(self.n_points), powA)
        self.data_chann[2].set_data(np.arange(self.n_points), powB)
        
        return self.data_chann










        



