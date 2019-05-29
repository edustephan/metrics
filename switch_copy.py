import paramiko
import time
import datetime
import warnings


ts = time.time()
today = datetime.datetime.fromtimestamp(ts).strftime('%m/%d/%Y')
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

class Switch:
    ip = ""
    name = ""

    def __init__(self,ip,name):
        self.ip = ip
        self.name = name

switches = []

switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))
switches.append(Switch("","NAME"))


class DataCollection:
    def __init__(self,ip,name):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(switch.ip, username="", password="")
        
        print("Date: ", today)

        stdin, stdout, stderr = ssh.exec_command('switchname')
        for swname in stdout:
            if swname != '':
                swname = swname.rstrip()
                switchname = swname
            else:
                break
        print("Switch Name: ",switchname)

        stdin, stdout, stderr = ssh.exec_command('mapsdb --show all -day {}'.format(today))
        # these lines will filter only RX(%), TX(%) and UTIL(%) from the command mapsdb
        # Next steps is remove RX,TX and UTIL entries and separate port number and port value
        # Eg: 1/0(43.17) will become port 1/0 with RX value of 43.17
        keep_print = False
        util = []
        for status in stdout:
            if keep_print or "UTIL(%)" in status:
                line = [splits for splits in status.split(' ')]
                line = list(filter(None, line))
                if not status.startswith("BN_SECS(Seconds)"):
                    if line[0] == ("UTIL(%)"):
                        line.remove(line[0])
                    #print(line)
                    util.append(line[0])
                    keep_print = True
                else:
                    break
        util = [i.split('(') for i in util] # split using '(' as index
        # next lines will remove ')' from end of list
        utilF = list(filter(lambda x: len(x) > 1,util))
        s = 0 
        while s < (len(utilF)):
            utilF[s][1] = (utilF[s][1].replace(')', ''))
            s += 1
        #Convert nested list to dict
        d = {k:row[0] for row in utilF for k in row[1:]}
    
        #Prepare data to be inserted in db
        pn = []
        for x in range(len(utilF)):
            x = str(x+1)
            pn.append("PortNumber"+x)
        pn = (', '.join(pn))
        pv = []
        for x in range(len(utilF)):
            x = str(x+1)
            pv.append("PortValue"+x)
        pv = (', '.join(pv))
        
        columns = ', '.join(map(str, d.keys()))
        values = ', '.join(map(repr, d.values()))
        #Checking INSERT command
        print("INSERT INTO table ({}) VALUES ({})".format(pn, values))
        print("INSERT INTO table ({}) VALUES ({})".format(pv, columns))

        stdin, stdout, stderr = ssh.exec_command('mapsdb --show details -day {} | grep "Switch Resource"'.format(today))
        for cpu in stdout:
            cpu = [splits for splits in cpu.split('|')]
            cpu = list(filter(None, cpu))
        
        if not (cpu[1]).startswith("In operating range"):
            print("CPU Status: ",cpu[5])
        else:
            print("CPU Status: ",cpu[1])

        stdin, stdout, stderr = ssh.exec_command('switchshow -portcount')
        for portcount in stdout:
            if portcount != '':
                portcount = [splits for splits in portcount.split(' ')]
                portcount = list(filter(None, portcount))
                qtport = (portcount[3]).rstrip()
                print("Total Ports: ",qtport)

        stdin, stdout, stderr = ssh.exec_command('switchshow')
        printport = False
        portonline = 0
        portnotonline = -1
        for swshow in stdout:
            if printport or "=" in swshow:
                if swshow != '':
                    swshow = [splits for splits in swshow.split(' ')]
                    swshow = list(filter(None, swshow))
                    
                    if not any([y in "Online" for y in swshow]) and not any([y in "No_Module" for y in swshow]):
                        portnotonline += 1
                        #print(swshow, portnotonline)

                    if any([x in 'Online' for x in swshow]):
                        portonline += 1
                        #print(swshow, portonline)

                    printport = True
                else:
                    break
        print("Online Ports: ",portonline)
        print("Not Online Ports: ",portnotonline)




for switch in (switches):
    DataCollection(switch.ip,switch.name)


