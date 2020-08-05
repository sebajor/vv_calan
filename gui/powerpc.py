import telnetlib, os, time


def PPC_upload_code(roachIP, file_path='ppc_save'):
    """Upload the required files to the ppc in the ROACH
    We connect through telnet to the 
    """
    user = 'root'
    tn = telnetlib.Telnet(roachIP)         
    tn.read_until("login: ")
    tn.write(user + "\n")
    tn.read_very_eager()
    time.sleep(1)
    tn.write('cd /var/tmp\n')
    time.sleep(2) 
    tn.read_very_eager()
    time.sleep(1)
    tn.write('rm *\n')
    time.sleep(2)
    tn.read_very_eager()
    for i in range(3):
        time.sleep(1)
        tn.write('nc -l -p 1234 > ppc_save \n')
        time.sleep(0.5)
        os.system('nc -w 3 '+str(roachIP)+' 1234 < '+file_path)
        time.sleep(1) 
        tn.read_very_eager()
        time.sleep(1)
        tn.write("find . -name ppc_save \n")
        time.sleep(0.5)
        ans = tn.read_very_eager()
        if(ans.find("ppc_save")!=-1):
            break    
    if(i==3):      
        raise RuntimeError('The file couldnt get upload..')
    time.sleep(1)
    tn.read_very_eager()
    time.sleep(1)
    tn.write('chmod +x ppc_save \n')
    time.sleep(1)
    tn.read_very_eager()
    tn.write('touch save \n')
    time.sleep(1)
    tn.read_very_eager()
    tn.close()
        
        


def PPC_start_measure(roachIP, read_cycles):
    user = 'root'
    tn = telnetlib.Telnet(roachIP)
    tn.read_until("login: ")
    tn.write(user + "\n")
    time.sleep(0.5)
    tn.read_very_eager()
    time.sleep(1)
    tn.write('cd /var/tmp\n')
    time.sleep(1)
    tn.read_very_eager()
    tn.write('busybox nohup ./ppc_save '+str(read_cycles+1)+' &\n')
    time.sleep(1)
    tn.read_very_eager()
    time.sleep(1)
    tn.write('busybox pgrep ppc_save \n')
    time.sleep(1)
    pid = tn.read_very_eager()
    time.sleep(1)
    tn.close()
    
    ind1 = pid.find('\n')
    ind2 = pid[ind1+1:].find('\n')
    
    
    return pid[ind1+1:ind1+ind2]



def PPC_download_data(roachIP,pc_IP):
    """
    """
    user = 'root'
    tn = telnetlib.Telnet(roachIP)
    tn.read_until("login: ")
    tn.write(user + "\n")
    time.sleep(1)
    tn.read_very_eager()
    tn.write('cd /var/tmp\n')
    time.sleep(3)
    tn.read_very_eager()
    os.system('nc -l -p 1234 > raw_data &') ##using without & works....but the system hungs waiting for the connection in the following line :(, could be a problem in the network settings
    tn.write('busybox nohup nc -w 3 '+str(pc_IP)+' 1234 < save &\n')
    time.sleep(3)
    tn.read_very_eager()
    tn.close()    
"""
    user = 'root'
    tn = telnetlib.Telnet(roachIP)
    tn.read_until("login: ")
    time.sleep(1)
    tn.write(user + "\n")
    tn.read_very_eager()
    time.sleep(2)
    tn.write('cd /var/tmp \n')
    time.sleep(2)
    tn.read_very_eager()
    time.sleep(2)
    os.system('nc -l 1234 > raw_data & \n')
    tn.write('busybox nohup nc -w 3 '+str(pc_IP)+' 1234 < save & \n')
    time.sleep(3)
    tn.read_very_eager()
    time.sleep(3)
    tn.close()
"""

def PPC_kill_process(roachIP, pid):
    user = 'root'
    tn = telnetlib.Telnet(roachIP)
    tn.read_until("login: ")
    tn.write(user + "\n")
    time.sleep(1)
    tn.read_very_eager()
    
    for i in range(3):
        tn.write("ps | grep *./ppc_save* \n")
        time.sleep(1)
        ans = tn.read_very_eager()
        print(ans)
        if(ans.find('ppc_save')!=-1):
            break
    
    if(i==3):
        print("The process has already finished")
        return
    else:
        tn.write('kill '+str(pid)+' \n')
        time.sleep(1)
        tn.write("ps | grep *./ppc_save* \n")
        time.sleep(1)
        ans = tn.read_very_eager()
        print('ps output: '+ans)
        return 


def PPC_check_status(roachIP, pid):
    ##IT HAS A BUG, IT RECOGNICE THE PS | GREP PPC_SAVE AS RUNNING APP..JAJA
    ###I HAD THE PID---> WE COULD USE IT!!!!
    
    user = 'root'
    tn = telnetlib.Telnet(roachIP)
    tn.read_until("login: ")
    tn.write(user + "\n")
    time.sleep(1)
    tn.read_very_eager()

    for i in range(3):
        #tn.write("ps | grep *./ppc_save* \n")
        tn.write("busybox pgrep ./ppc_save* \n")
        time.sleep(1)
        ans = tn.read_very_eager()
        print(ans)
        if(str(pid) in ans):
            print('Process running')
            return 1
    print('Process not found')
    return 0
            
    







