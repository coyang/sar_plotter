#!/usr/bin/env python
import operator
import os, sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import plotly.plotly as py
import plotly.tools as tls

procs = []
cswitch = []
CPU_all = []
interupts = []
tps = []
network = []
memory = []

def plot_all_the_things(l,n,e):
    for i in xrange(len(e)):
        l.sort(key=operator.itemgetter(0))
        y = np.array([item[1+i] for item in l])
        x = np.array([datetime.fromtimestamp(item[0]) for item in l])

        if '%' in e[i]:
            plt.ylim([0,100])

        plt.plot(x,y)
        plt.xlabel('time')
        plt.xticks(rotation=90)
        plt.ylabel(e[i])
        plt.tight_layout()

        fig = plt.gcf()
        #plt.show()
        plt.savefig(n+'-'+e[i])
        plt.clf()
    #plotly_fig = tls.mpl_to_plotly( fig )

    #plotly_url = py.plot(plotly_fig, filename='test')

def normalize_time(v,w):
    x = str(v) + '-' + str(w)
    utc_time = datetime.strptime(x, "%Y-%m-%d-%H:%M:%S")
    return int((utc_time - datetime(1970,1,1)).total_seconds())

if __name__ == "__main__":
    state = 'proc'

    for f in os.listdir('data'):
        try:
            h = open('data/'+f)
        except:
            print 'Unable to open data file ' + f
            sys.exit(1)

        data = h.readlines()
        date = data[0].strip().split("\t")[-1]
        print date

        for line in data:
            line = line.strip()
            if 'mandalorian' in line:
                pass
            elif line == '':
                pass
            elif 'Average' in line:
                pass
            # Here comes to ugly part
            elif 'proc/s' in line:
                state = 'proc'
                pass
            elif 'cswch/s' in line:
                state = 'cswitch'
            elif 'CPU     %user     %nice' in line:
                state = 'CPU_ALL'
            elif 'INTR    intr/s' in line:
                state = 'interrupts'
            elif 'CPU  i000/s  i001/s  i008/s' in line:
                state = 'skip'
            elif 'tps      rtps      wtps' in line:
                state = 'tps'
            elif 'frmpg/s   bufpg/s   campg/s' in line:
                state = 'skip'
            elif 'TTY   rcvin/s   xmtin/s framerr/s' in line:
                state = 'skip'
            elif 'IFACE   rxpck/s   txpck/s   rxbyt/s' in line:
                state = 'network'
            elif 'IFACE   rxerr/s   txerr/s    coll/s' in line:
                state = 'skip'
            elif 'call/s retrans/s    read/s' in line:
                state = 'skip'
            elif 'scall/s badcall/s  packet/s' in line:
                state = 'skip'
            elif 'pgpgin/s pgpgout/s   fault/s' in line:
                state = 'skip'
            elif 'kbmemfree kbmemused  %memused' in line:
                state = 'memory'
            elif 'dentunusd   file-sz  inode-sz' in line:
                state = 'skip'
            elif 'totsck    tcpsck' in line:
                state = 'skip'
            elif 'runq-sz  plist-sz   ldavg-1' in line:
                state = 'skip'
            else:
                d = filter(None,line.split(" "))
                d[0] = normalize_time(date, d[0])
                if state == 'proc':
                    procs.append([float(i) for i in d])
                elif state == 'cswitch':
                    cswitch.append([float(i) for i in d])
                elif state == 'CPU_ALL':
                    if 'all' in line:
                        d = [d[0]] + d[2:]
                        CPU_all.append([float(i) for i in d])
                elif state == 'interrupts':
                    d = [d[0], d[2]]
                    interupts.append([float(i) for i in d])
                elif state == 'tps':
                    tps.append([float(i) for i in d])
                elif state == 'network':
                    if 'eth0' in line:
                        d = [d[0]] + d[2:]
                        network.append([float(i) for i in d])
                elif state == 'memory':
                    memory.append([float(i) for i in d])
                else:
                    pass

        h.close()
    plot_all_the_things(CPU_all,'CPU Utilization',['%user', '%nice', '%system', '%iowait', '%steal', '%idle'])
    plot_all_the_things(procs,'Process per secs',['proc per s'])
    plot_all_the_things(cswitch,'Context Switch',['cswch per s'])
    plot_all_the_things(interupts,'Interrupts',['intr per s'])
    plot_all_the_things(tps, 'Transactions per second', ['tps','rtps','wtps','bread per s','bwrtnpe rs'])
    plot_all_the_things(network, 'Network IO (eth0)', ['rxpck per s','txpck per s','rxbyt per s','txbyt per s','rxcmp per s','txcmp per s','rxmcst per s'])
    plot_all_the_things(memory, 'Memory Usage', ['kbmemfree','kbmemused','%memused','kbbuffers','kbcached','kbswpfree','kbswpused','%swpused','kbswpcad'])
