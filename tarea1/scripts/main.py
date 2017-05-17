# Copyright (c) 2017 
# Authors: Daniel Garcia Vaglio, Esteban Zamora Alvarado

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import sys, getopt
from multiprocessing import Pipe, Process, JoinableQueue
from parser import get_addresses
from core import core
from cacheL1 import cacheL1
from cacheL2 import cacheL2
from mem import mem
from utils import *

def option_parser(argv):
    core1_file="mem_trace_core1.txt"
    core2_file="mem_trace_core2.txt"
    debug=False
    core1_sprint=3
    core2_sprint=1
    output_file = None
    simulation_quant=1
    
    if "--debug" in argv:
        debug=True

    if "--help" in argv:
        tab="\n"+" "*4
        print "Options: \n"
        print "--help   Prints this text and exit"
        print
        print "--debug  Activate debug information"
        print
        msg = "--generate_random=<file size>, <file name>, optional:(<file size>, <file name>)"+tab
        msg += "Generate a file with random instructions for tests of specific size and name and then exit"+tab
        msg += "Examples 1: --generate_random=200,a_file"+tab
        msg += "         2: --generate_random=200,a_file,100,an_optional_file"
        
        print msg
        print
        print "--ratio: n:m <cores ratio execution> "+tab+"(Default is 3:1)"
        print
        print "--core1_file=<file name>"+tab+"File where core1 instructions are taken from"+tab+"(Default is 'mem_trace_core1.txt')"
        print
        print "--core2_file=<file name>"+tab+"File where core2 instructions are taken from"+tab+"(Default is 'mem_trace_core2.txt')"
        print
        print "--output_file=<file name>"+tab+"File to store output"+tab+"(Default is to print output to terminal)"
        print
        print "--run_n=<integer>"+tab+"Run n simulations and get statistics about miss and hit rate"+tab+"Output file will be ignored"
        sys.exit(0)
        
        
    for argument in argv:
        if "--ratio=" in argument:
            cores_sprints=argument.split("=")[1]
            core1_sprint=int(cores_sprints.split(":")[0])
            core2_sprint=int(cores_sprints.split(":")[1])
        if "--core1_file=" in argument:
            core1_file=argument.split("=")[1]
        if "--core2_file=" in argument:
            core2_file=argument.split("=")[1]
        if "--output_file=" in argument:
            output_file =argument.split("=")[1]
        if "--generate_random=" in argument:
            options=argument.split("=")[1].split(",")
            if len(options)==2:
                random_generator(int(options[0]), options[1])
            elif len(options)==4:
                random_generator(int(options[0]), options[1], int(options[2]), options[3])
            sys.exit(0)
        if "--run_n=" in argument:
            options=argument.split("=")[1]
            simulation_quant=int(options)
            
            
    return [debug, core1_file, core2_file, core1_sprint, core2_sprint, output_file, simulation_quant]


def print_fn(filename=None, print_queue=None, sig_kill=None):
    if filename is not None: file_handle = open(filename, "w", 0)
    while (True):
        try:
            msg = print_queue.get(block=True)
            if filename is not None:
                print >>file_handle, msg
            else: print msg
            print_queue.task_done()
        except:
            break
        
    if filename is not None: file_handle.close()
    
    

def run_simulation(debug=False, instructions_list_core_1=[], instructions_list_core_2=[], core1_sprint=3, core2_sprint=1, output_file=None):
    
    #Create the pipe connections (ports)

    #-------Communication between L1 cache and cores----------
    #cmd core->cacheL1
    [cmd_cache1_from_core1, cmd_core1_to_cache1]=Pipe(False)
    [cmd_cache2_from_core2, cmd_core2_to_cache2]=Pipe(False)
    #data cacheL1->core
    [data_core1_from_cache1, data_cache1_to_core1]=Pipe(False)
    [data_core2_from_cache2, data_cache2_to_core2]=Pipe(False)
    #data core->cacheL1
    [data_cache1_from_core1, data_core1_to_cache1]=Pipe(False)
    [data_cache2_from_core2, data_core2_to_cache2]=Pipe(False)
    
    #-------Communication between L1 cache and L2 cache-------
    #cmd cacheL1->cacheL2
    [cmd_L2_from_L1, cmd_L1_to_L2]=Pipe(False)
    #data cacheL1->cacheL2
    [data_L2_from_L1, data_L1_to_L2]=Pipe(False)
    #data cacheL2->cacheL1
    [data_L1_from_L2, data_L2_to_L1]=Pipe(False)

    
    #-------Communication between L2 cache and main memory----
    #cmd cacheL2->Mem
    [cmd_mem_from_cache, cmd_cache_to_mem]=Pipe(False)
    #data cacheL2->Mem
    [data_mem_from_cache, data_cache_to_mem]=Pipe(False)
    #data Mem->cacheL2
    [data_cache_from_mem, data_mem_to_cache]=Pipe(False)

    #------Port with sigkill, for last state storage---------
    [sig_kill_from_core, sig_kill]=Pipe(False)
    [last_state_from_cacheL1, last_state_to_main]=Pipe()
    [last_state_from_cacheL2, last_state_to_main2]=Pipe()

    
    #Parameters in dictionaries for each module
    core_parameters={"instructions_core1":instructions_list_core_1,
                     "cmd_to_cache1":cmd_core1_to_cache1,
                     "data_from_cache1":data_core1_from_cache1,
                     "data_to_cache1":  data_core1_to_cache1,
                     "instructions_core2":instructions_list_core_2,
                     "cmd_to_cache2": cmd_core2_to_cache2,
                     "data_from_cache2": data_core2_from_cache2,
                     "data_to_cache2":  data_core2_to_cache2} 

    cacheL1_parameters={"cmd_from_core1":cmd_cache1_from_core1,
                        "cmd_from_core2": cmd_cache2_from_core2,
                        "data_from_core1": data_cache1_from_core1,
                        "data_from_core2": data_cache2_from_core2,
                        "data_to_core1": data_cache1_to_core1,
                        "data_to_core2": data_cache2_to_core2,
                        "cmd_to_cache": cmd_L1_to_L2,
                        "data_to_cache": data_L1_to_L2,
                        "data_from_cache":data_L1_from_L2}

    cacheL2_parameters={"cmd_from_cache": cmd_L2_from_L1,
                        "data_from_cache": data_L2_from_L1,
                        "data_to_cache": data_L2_to_L1,
                        "cmd_to_mem": cmd_cache_to_mem,
                        "data_to_mem": data_cache_to_mem,
                        "data_from_mem":data_cache_from_mem}

    mem_parameters={"cmd_from_cache": cmd_mem_from_cache,
                    "data_from_cache": data_mem_from_cache,
                    "data_to_cache": data_mem_to_cache}

    #Print communication queue
    print_queue = JoinableQueue()
    
    #Create the processes
    core_p = Process(target=core, args=(core_parameters, debug,
                                        core1_sprint, core2_sprint, print_queue, sig_kill)) #Instructions ratio core1:core2
    cacheL1_p = Process(target=cacheL1, args=(cacheL1_parameters, debug, print_queue, sig_kill_from_core, last_state_from_cacheL1))
    cacheL2_p = Process(target=cacheL2, args=(cacheL2_parameters, debug, print_queue, sig_kill_from_core, last_state_from_cacheL2))
    mem_p = Process(target=mem, args=(mem_parameters, debug, print_queue, sig_kill_from_core))
    print_p = Process(target=print_fn, args=(output_file, print_queue, sig_kill_from_core))
    
    #Process management
    print_p.start()
    core_p.start()
    cacheL1_p.start()
    cacheL2_p.start()
    mem_p.start()
    
    core_p.join()
    print_queue.join()
    cacheL1_p.join()
    cacheL2_p.join()
    mem_p.join()
    
    sleep(0.1)#really be sure, every process has terminated
    print_p.terminate()
    cacheL1_last_state=last_state_to_main.recv()
    cacheL2_last_state=last_state_to_main2.recv()

    return {"L1(1)":cacheL1_last_state[0], "L1(2)":cacheL1_last_state[1], "L2":cacheL2_last_state}

def main(argv):
    [debug, core1_file, core2_file, core1_sprint,core2_sprint, output_file, simulation_quant]=option_parser(argv)
    #Get the instructions from files
    instructions_list_core_1=get_addresses(core1_file)
    instructions_list_core_2=get_addresses(core2_file)

    if simulation_quant==1:
        noting=run_simulation(debug, instructions_list_core_1, instructions_list_core_2,
                              core1_sprint, core2_sprint, output_file)

    else:
        #run many simulations at once. Fisrt divide the isntructions for every simulation
        partitioned_ins_list_core_1=partition_n(instructions_list_core_1, simulation_quant)
        partitioned_ins_list_core_2=partition_n(instructions_list_core_2, simulation_quant)
        last_states=[]
        for sim in xrange(simulation_quant):
            print "\n****************"*8
            last_states.append(run_simulation(debug, partitioned_ins_list_core_1[sim],
                                              partitioned_ins_list_core_2[sim],
                                              core1_sprint, core2_sprint, None) )# no output file

        print "\n\n"+"="*20+"\nFinished "+str(simulation_quant)+" simulations, with "+str(int(len(instructions_list_core_1)/simulation_quant))+" instructions each."
        averages=get_last_state_averages(last_states)

 

if __name__=="__main__":
    main(sys.argv)
