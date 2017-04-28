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

from multiprocessing import Pipe, Process, Queue
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
    
    if "--debug" in argv:
        debug=True

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
            
    return [debug, core1_file, core2_file, core1_sprint, core2_sprint, output_file]


def print_fn(filename, print_queue):
    if filename is not None:
        file_handle = open(filename, "w")
    while True:
        try:
            msg = print_queue.get(block = False)
            if filename is not None:
                print >>file_handle, msg
            else:
                print msg
        except:
            break


def main(argv):
    [debug, core1_file, core2_file, core1_sprint,core2_sprint, output_file]=option_parser(argv)
    
    #Get the instructions from files
    instructions_list_core_1=get_addresses(core1_file)
    instructions_list_core_2=get_addresses(core2_file)

    
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
    print_queue = Queue()
    
    #Create the processes
    print_p = Process(target=print_fn, args=(output_file, print_queue))
    core_p = Process(target=core, args=(core_parameters, debug,
                                        core1_sprint, core2_sprint, print_queue)) #Instructions ratio core1:core2
    cacheL1_p = Process(target=cacheL1, args=(cacheL1_parameters, debug, print_queue))
    cacheL2_p = Process(target=cacheL2, args=(cacheL2_parameters, debug, print_queue))
    mem_p = Process(target=mem, args=(mem_parameters, debug, print_queue))

    #Process management
    print_p.start()
    core_p.start()
    cacheL1_p.start()
    cacheL2_p.start()
    mem_p.start()
    
    core_p.join()
    
    print_p.terminate()
    cacheL1_p.terminate()
    cacheL2_p.terminate()
    mem_p.terminate()


if __name__=="__main__":
    main(sys.argv)
