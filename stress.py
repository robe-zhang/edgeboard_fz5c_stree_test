#!/usr/bin/python3

import os
import time
import subprocess
from decimal import Decimal
from multiprocessing import Process

top_dir = os.path.dirname(os.path.abspath(__file__))

# 0xFFA50800	PS System Monitor
# 0xFFA50C00	PL System Monitor
# subprocess.run("ls -al", shell=True)

def get_temperature(address):
    datafile = os.popen("devmem %s" % address)
    rawdata = int(datafile.readline().strip(),16)
    result = "%.2f" %(Decimal(rawdata) * Decimal(509.3140064) / Decimal(65535) - Decimal(280.23087870))
    return result

def get_cpustatus():
    datafile = os.popen("top -b -n 1 | grep 'Cpu(s):'")
    result = datafile.readline().strip()
    return result

def get_time():
    datafile = os.popen("date +%F' '%T' '%z")
    result = datafile.readline().strip()
    return result

def get_log():
    result = "%s  %s  PS temperature: %s C.  PL temperature: %s C." %(get_time(),get_cpustatus(),get_temperature(address = "0xFFA50800"),get_temperature(address = "0xFFA50C00"))
    return result

def function_log(logfile, during):
    while True:
        print("==== Process log   <%s> is running ====" %os.getpid())
        writefile = open("%s/%s"%(top_dir,logfile),"a")
        logdata = "%s" %get_log()
        print(logdata)
        writefile.write("%s\n" %logdata)
        writefile.close()
        time.sleep(during)

def function_build(builddir):
    while True:
        print("==== Process build <%s> is running ====" %os.getpid())
        build_dir = "%s/%s" %(top_dir,builddir)
        subprocess.run("mkdir -p %s" %build_dir, shell=True )
        os.chdir("%s" %build_dir)
        subprocess.run("rm -rf *" , shell=True)
        subprocess.run("cmake /home/root/workspace/PaddleLiteSample/classification" , shell=True)
        subprocess.run("make", shell=True )
        os.chdir("%s" %top_dir)

def function_ai(builddir):
    print("==== Process AI    <%s> is running ====" %os.getpid())
    build_dir = "/home/root/workspace/PaddleLiteSample/classification/%s" %builddir
    subprocess.run("mkdir -p %s" %build_dir, shell=True )
    os.chdir("%s" %build_dir)
    subprocess.run("rm -rf *" , shell=True)
    subprocess.run("cmake /home/root/workspace/PaddleLiteSample/classification" , shell=True)
    subprocess.run("make", shell=True )
    while True:
        print("==== Process AI    <%s> is running ====" %os.getpid())
        subprocess.run("./image_classify ../configs/resnet50/drink.json" , shell=True)
    os.chdir("%s" %top_dir)

def program_stress_test(idle_time, stress_time, idle2_time, logfile, during, processes, builddir):
    file_log = "%s/%s"%(top_dir,logfile)
    writefile = open("%s"%file_log,"a")
    writefile.write("==============================================================================================================================================================\n")
    writefile.write("idle: %s S.  stree: %s S.  idle2: %s S.  logfile: %s/%s.  processes: %s.\n" %(idle_time, stress_time, idle2_time, top_dir, logfile, processes))
    writefile.write("==============================================================================================================================================================\n")
    writefile.close()
    process_log = Process(target = function_log, args =(logfile, during, ), name = "worker_log" )
    process_log.start()
    time.sleep(idle_time)
    record = []
    for i in range(processes):
        if  ( i == 0 ):
            process_work = Process(target = function_ai, args =("build",), name = "worker_ai" )
        else:
            process_work = Process(target = function_build, args =("%s_%s"%(builddir,i),), name = "worker_%s"%i )
        process_work.start()
        record.append(process_work)
    time.sleep(stress_time)
    for process_work in record:
        process_work.terminate()
    for process_work in record:
        process_work.join()
    time.sleep(idle2_time)
    process_log.terminate()
    process_log.join()
    for i in range(processes):
        subprocess.run("rm -rf %s/%s_%s " %(top_dir,builddir,i ) , shell=True)
    record.clear()
        
if __name__ == '__main__':
    program_stress_test(idle_time = 1800, stress_time= 3600, idle2_time = 1800, logfile = "stress.log", during = 5, processes = 6, builddir = "worker")




