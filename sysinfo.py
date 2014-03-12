# -*- coding: utf-8 -*-
'''
Module to get sysinfo with tool sysstat(sar)
'''

import os
import re
import subprocess
import commands

def _check_sar():
    (state, output) = commands.getstatusoutput('which sar')
    if state != 0:
        raise Exception("cmd sar can not be found")

    return output

def show(freq='6',sar='/usr/bin/sar'):
    sar_opt = {
        'CPU': {'opt': '-u -P ALL', 'key': 'CPU'},
	'MEM': {'opt': '-r', 'key': 'kbmemfree'},
        'LOADAVG': {'opt': '-q', 'key': 'runq-sz'},
        'NETWORK': {'opt': '-n DEV', 'key': 'IFACE'},
        'SOCKET': {'opt': '-n SOCK', 'key': 'totsck'},
    }
    sarp = _check_sar()
    sarp.strip()
    if sarp != sar: sar = sarp
    sar_string = _sar_run(sar, sar_opt, freq)
    sar_data = _sar_parse(sar_string, sar_opt)

    return sar_data

def _sar_run(sar, sar_opt, freq):
    sar_env = os.environ
    sar_env['LANG'] = 'en'
    sar_env['S_TIME_FORMAT'] = 'ISO'
    sar_cmd = []

    sar_cmd.append(sar)
    for k,v in sar_opt.items():
        sar_cmd.extend(v['opt'].split(' '))
    sar_cmd.append(freq)
    sar_cmd.append('1')
    sar_run = subprocess.Popen(sar_cmd, stdout = subprocess.PIPE, env = sar_env)

    return sar_run.stdout.readlines()

def _sar_parse(sar_data,sar_opt):
    flag_ave = 0
    item = {}
    item_list = []
    re_ave = re.compile("^Average:\s+")
    re_space = re.compile("\s+")

    for line in sar_data:
        if not flag_ave and re.match(re_ave, line): flag_ave = 1
        if not flag_ave: continue
        llist = re.split(re_space, line)
        if llist[0] == '':
            (name, data) = _sar_item(sar_opt, item_list)
            item[name] = data
            item_list = []
            continue
        else:
            del llist[0]
            item_list.append(llist)

    if len(item_list) != 0:
        (name, data) = _sar_item(sar_opt, item_list)
        item[name] = data

    return item
       
def _sar_item(sar_opt, item_list):
    name = ''
    for k,v in sar_opt.items():
       if sar_opt[k]['key'] == item_list[0][0]:
           name = k
           break
    if name == '':
        raise Exception("can not find {0} in sar_opt".format(item_list[0][0]))

    data = {}
    if len(item_list) == 2:
        for i in range(len(item_list[0]) -1):
            if item_list[0][i] != '' and item_list[1][i] != '':
                data[item_list[0][i]] = item_list[1][i]
    else:
        legend = item_list[0]
        del legend[0]
        del item_list[0]

        for i in item_list:
            data[i[0]] = tmp = {}
            del i[0]
            for j in range(len(legend) -1):
                tmp[legend[j]] = i[j]

    return (name, data)
