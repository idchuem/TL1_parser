# -*- coding: cp949 -*-
#!/opt/liko/bin/python

import sys
import telnetlib
import time

class Telnet(telnetlib.Telnet, object):
    if sys.version > '3':
        def read_until(self, expected, timeout=None):
            expected = bytes(expected, encoding='utf-8')
            received = super(Telnet, self).read_until(expected, timeout)
            return str(received, encoding='ms949', errors='ignore')

        def write(self, buffer):
            buffer = bytes(buffer, encoding='utf-8')
            super(Telnet, self).write(buffer)

        def expect(self, list, timeout=None):
            for index, item in enumerate(list):
                list[index] = bytes(item, encoding='utf-8', errors='ignore')
            match_index, match_object, match_text = super(Telnet, self).expect(list, timeout)
            return match_index, match_object, str(match_text, encoding='utf-8')

def now_time() :
    now= time.localtime()
    if int(now.tm_mon) <10 :
      mon=str('0')+str(now.tm_mon)
    else :
      mon=now.tm_mon
    if int(now.tm_mday) <10 :
      day=str('0')+str(now.tm_mday)
    else :
      day=now.tm_mday
    if int(now.tm_hour) <10 :
      hour=str('0')+str(now.tm_hour)
    else :
      hour=now.tm_hour
    if now.tm_min <10 :
      min=str('0')+str(now.tm_min)
    else :
      min=now.tm_min
#  now_date= str(now.tm_year)+str(mon)+str(day)+str(hour)+str(min)
    now_date= str(mon)+str(day)
    return(now_date)

def getNeip ():
    IP=[]
    f=open('NE_IP', encoding='utf-8')
    for line in f.read().split():
        IP.append(line)
    f.close()
    return(IP)

def getNeid ():
    telnet = Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:' + hostnames + ':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-CRS-VT2:' + hostnames + ':ALL:CTAG:::,;')
    Logs = telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' Alarm Parsing Completed!')
    telnet.write('CANC-USER:' + hostnames + ':ADMIN:CTAG;')
    telnet.close()

def SONET_TO_STM(SONET) :
     #VT2-SHELF-SLOT-PORT-AUG-TUG-AU-TU
    SONET_Split=SONET.split('-') # SONET �溸(SHELF-SLOT-PORT-AUG-TUG)�� - ������ �ɰ� ����Ʈ�� ����
    SDH_Temp = "" # SDH��ȯ�� ���� �ӽ� ���� ����
    n = 0
    if (len(SONET_Split)>4) :
        SONET_Split[1]='#'+SONET_Split[1]
        SONET_Split[2]='SL'+SONET_Split[2]
        SONET_Split[3]='P'+SONET_Split[3]
        SONET_Split[4]='AUG'+str((int(SONET_Split[4])+2)/3) #(SONET����-> SDH��ȯ)
        SONET_Split[0]=SONET_Split[0].replace('VT2AU4','VC12')
        SONET_Split[0]=SONET_Split[0].replace('STS3C', 'VC4')
        SONET_Split[0]=SONET_Split[0].replace('STS1AU4', 'VC3')
        while(len(SONET_Split)-n) : # �ɰ��� �溸 ���̸�ŭ �ݺ�
            SDH_Temp=SDH_Temp+SONET_Split[n]+'-' #��ȯ�� SDH �溸�� �ٽ� �� ����
            n=n+1

    else : # TUG�� ���°��(SONET_Split[4] �� ���� �溸)
        SONET_Split[0] = SONET_Split[0].replace('OC256', 'STM64')
        SONET_Split[0] = SONET_Split[0].replace('OC48', 'STM16')
        SONET_Split[0] = SONET_Split[0].replace('OC12', 'STM4')
        SONET_Split[0] = SONET_Split[0].replace('OC3', 'STM1')
    while(len(SONET_Split)-n) :# �ɰ��� �溸 ���̸�ŭ �ݺ�
        SDH_Temp=SDH_Temp+SONET_Split[n]+'-' #��ȯ�� SDH �溸�� �ٽ� �� ����
        n=n+1
    SDH=SDH_Temp[0:len(SDH_Temp)-1] #���� ��ȯ�� SDH�溸���� '-' text�����ϱ� ���� ����
    return(SDH)

def getCrs(hostnames,NE_IP) : #[���] �ڳ� �� Log Parsing

    telnet =Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:'+hostnames+':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-CRS-VT2:'+hostnames+':ALL:CTAG:::,;')
    Logs=telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' Alarm Parsing Completed!')
    telnet.write('CANC-USER:'+hostnames+':ADMIN:CTAG;')
    telnet.close()

    return Logs

def getAlms(hostnames,NE_IP) : #[���] �ڳ� �� Log Parsing

    telnet =Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:'+hostnames+':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-ALM-ALL:'+hostnames+':ALL:CTAG:::,;')
    Logs=telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' Alarm Parsing Completed!')
    telnet.write('CANC-USER:'+hostnames+':ADMIN:CTAG;')
    telnet.close()

    return Logs

#���θ��μ� �� ȭ���� �����ϸ� ���� �̺κк��� �����




NE_IP=getNeip()

for IP in NE_IP:

    location = []
    cause = []
    crs1 = []
    crs2 = []
    bothUneq = 0
    fromUneq = 0
    toUneq = 0
    bothNotUneq = 0


    alms = getAlms('',IP)
    alm = alms.split('   "')
    alm=alm[1:]

    for i in range(len(alm)):
        if alm[i][0]=='V':
            alm1 = alm[i].split(',')
            location.append(alm1[0])
            cause.append(alm1[2])

    crs=getCrs('', IP)
    crs=crs.split('   "')
    for i in range(len(crs)):
        if crs[i][0]=='V':
            crstmp = crs[i].split(',')
            crs1.append(crstmp[0])
            crs2.append(crstmp[1].split(':')[0])

    for i in range(len(crs1)):
        if (crs1[i] in location) and (crs2[i] in location):
                k=location.index(crs1[i])
                j=location.index(crs2[i])
                if cause[k]=='UNEQ' and cause[j]=='UNEQ':
                    bothUneq=bothUneq+1
                elif cause[k]=='UNEQ' and cause[j]!='UNEQ':
                    fromUneq = fromUneq + 1
                elif cause[k]!='UNEQ' and cause[j]=='UNEQ':
                    toUneq = toUneq + 1
                elif cause[k]!='UNEQ' and cause[j]!='UNEQ':
                    bothNotUneq = bothNotUneq + 1

    print(bothUneq)
    print(fromUneq+toUneq)
    print(+bothNotUneq)

