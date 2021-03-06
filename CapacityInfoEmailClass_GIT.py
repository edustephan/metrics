''' 
Collect: 
NL -  Raw space , Allocated , Allocated % , Free Space , Free Space % , Provisioned , Provisioned % 
FC -  Raw space , Allocated , Allocated % , Free Space , Free Space % , Provisioned , Provisioned % 
SSD - Raw space , Allocated , Allocated % , Free Space , Free Space % , Provisioned , Provisioned % 
'''
from shutil import copyfile
from pathlib import Path
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko


class DataCollection:
    def __init__(self,host,ip,dev):
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh.connect(ip, username="YOUR_USER", password="YOUR_PASS")
            comm = 'showpd -p -devtype ' + dev
            exists = Path("%s.html" % (host))
            if not exists.is_file():
                copyfile("template.html", "%s.html" % (host))

            s = open("%s.html" % (host)).read()

            stdin, stdout, stderr = ssh.exec_command(comm)
            while True:
                line = (stdout.readline()).rstrip()
                if line != '':
                    if 'total' in line:
                        line = [splits for splits in line.split(' ')]
                        line = list(filter(None, line))
                        
                        RAW = line[2]
                        FREE = line[3]
                        RAW = int(RAW)/1024
                        FREE = int(FREE)/1024
                        FREP = FREE/RAW
                        
                        RAW = ("{:,}".format(RAW))
                        FREE = ("{:,}".format(FREE))
                        FREP = ("{0:.2%}".format(FREP))

                        s = s.replace('ARRAY_NAME', host)
                        if dev == 'FC':
                            s = s.replace('FC_RAW', str(RAW))
                            s = s.replace('FC_FREE', str(FREE))
                            s = s.replace('FC_FREP', str(FREP))

                        if dev == 'SSD':
                            s = s.replace('SSD_RAW', str(RAW))
                            s = s.replace('SSD_FREE', str(FREE))
                            s = s.replace('SSD_FREP', str(FREP))

                        if dev == 'NL':
                            s = s.replace('NL_RAW', str(RAW))
                            s = s.replace('NL_FREE', str(FREE))
                            s = s.replace('NL_FREP', str(FREP))

                        f = open("%s.html" % (host), 'w')
                        f.write(s)
                        f.close()

                else:
                    break
           

class Array:
    ip = ""
    name = ""

    def __init__(self,ip,name):
        self.ip = ip
        self.name = name

arrays = []
arrays.append(Array("IP","HOST_NAME"))



dev_type = ['FC','SSD','NL']
for dev in dev_type:
    for host in (arrays):
        DataCollection(host.name,host.ip,dev)


for host in (arrays):
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(host.ip, username = 'YOUR_USER', password = 'YOUR_PASS')

    stdin, stdout, stderr = conn.exec_command('showsys')

    while True:
        line = (stdout.readline()).rstrip()
        if line != '':
            if host.name in line: 
                line = [splits for splits in line.split(' ')]
                line = list(filter(None, line))
                CAPA = int(line[8])/1024
        else:
            break

    stdin, stdout, stderr = conn.exec_command('showvv -space -tpvv')

    while True:
        line = (stdout.readline()).rstrip()
        if line != '':
            if 'total' in line:
                line = [splits for splits in line.split(' ')]
                line = list(filter(None, line))
                over = int(line[9])/1024
        else:
            break

    s = open("%s.html" % (host.name)).read()
    OVERP = over/CAPA
    CAPA = ("{:,}".format(CAPA))
    OVERP = ("{0:.2%}".format(OVERP))
    over = ("{:,}".format(over))
    
    s = s.replace('ARRAY_CAPAC', str(CAPA))
    s = s.replace('ARRAY_ALLOP', str(over))
    s = s.replace('ARRAY_ALLP', str(OVERP))
    f = open("%s.html" % (host.name), 'w')
    f.write(s)
    f.close()


    s = open("%s.html" % (host.name)).read()
    
    s = s.replace('FC_RAW', '--')
    s = s.replace('FC_FREE', '--')
    s = s.replace('FC_FREP', '--')

    s = s.replace('NL_RAW', '--')
    s = s.replace('NL_FREE', '--')
    s = s.replace('NL_FREP', '--')

    f = open("%s.html" % (host.name), 'w')
    f.write(s)
    f.close()



    with open("U:\\Activities\\code\\html\\email\\%s.html" % (host.name), 'r') as myfile:

        body=myfile.read()
        address_book = ['email@email.com', 'email@email.com']
        msg = MIMEMultipart()    
        sender = 'email@email.com'
        subject = "Capacity Report - %s" % (host.name)
        
        msg['From'] = sender
        msg['To'] = ','.join(address_book)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        text=msg.as_string()
        s = smtplib.SMTP('smtp.email.com')
        s.sendmail(sender,address_book, text)
        s.quit()

    os.remove("%s.html" % (host.name))
