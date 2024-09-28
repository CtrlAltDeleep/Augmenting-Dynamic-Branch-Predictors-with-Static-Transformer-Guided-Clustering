import os
import sys
import subprocess
from subprocess import Popen
import psutil
import random
import time

#run from base spec dir
base_dir = os.getcwd()
spec_path = "/home/ctrlaltdeleep/gem5/spec2006/"
gem5 = "/home/ctrlaltdeleep/gem5/"
benchmark = base_dir.split("/")[6]
specinvoke = subprocess.run([spec_path+"bin/specinvoke", "-n"], stdout=subprocess.PIPE)
random.seed(sum(ord(c) for c in base_dir))
commands = [line.decode().strip() for line in specinvoke.stdout.split(b"\n") if not line.startswith(b"#")]
procs = []
scaled_up = True
very_scaled = False

# iterate over all items in the current directory
for out_dir in os.listdir(base_dir):
    if os.path.isdir(out_dir) and out_dir.startswith("checkpoints.") and out_dir[-1].isdigit():
        command = commands[int(out_dir[-1])]
        cpt_number = 0
        for cpt_dir in os.listdir(os.path.join(base_dir, out_dir)):
            waited = 0
            finished = False
            # if this cpt_dir is a directory and its name starts with 'cpt.'
            if os.path.isdir(os.path.join(base_dir, out_dir, cpt_dir)) and cpt_dir.startswith('cpt.'):
                cpt_number += 1
                binary = spec_path+"benchspec/CPU/"+benchmark+"/run/run_peak_refspeed_mytest-64.0000/"+command.split()[0]
                if sys.argv[1] == 'base':
                    address_file = "/home/ctrlaltdeleep/empty"
                    O3outdir = "base."+out_dir[-1]+"/"+str(cpt_number)+".out"
                else:
                    address_file = binary+"_pnd_address"
                    O3outdir = "pnd."+out_dir[-1]+"/"+str(cpt_number)+".out"
                run = "ADDR_FILE="+address_file+" "+gem5+"build/ARM/gem5.opt --outdir="+O3outdir+" "+gem5+"configs/example/se.py --cpu-type=DerivO3CPU --caches --l2cache --restore-simpoint-checkpoint -r "+str(cpt_number)+" --checkpoint-dir "+out_dir+" --restore-with-cpu=AtomicSimpleCPU --mem-size=50GB -c "+binary+" --options=\""+' '.join(command.split()[1:])+"\""
                if scaled_up:
                    if very_scaled:
                        run += " --l1d_size=256KiB --l1i_size=256KiB --l2_size=4MB"
                    else:
                        run += " --l1d_size=128KiB --l1i_size=128KiB --l2_size=2MB"
                p = Popen(run, shell=True)
                procs.append(p)
                while waited < 60*1 and finished == False:
                    time.sleep(10)
                    waited += 10
                    if Popen.poll(p) != None:
                        finished = True
                time.sleep(random.uniform(0,1)*60)
                if psutil.virtual_memory().percent < 70 and psutil.cpu_percent() < 90: continue
                Popen.wait(p)
for p in procs:
    Popen.wait(p)
