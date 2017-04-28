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

from utils import *

def execute_n(ins_list_core=[], cmd_to_cache=None, data_to_cache=None,
              data_from_cache=None, counter_core=0, debug=False, limit=3,
              identity=0):
    count = 0
    while counter_core+count < len(ins_list_core) and count < limit:
        instruction = ins_list_core[counter_core+count]
        [address, command] = instruction
        if command == "{L}":
            print "\n--------------------------------------------------------------------------------------"
            print "CORE("+str(identity)+"): <I"+str(counter_core+count)+"> Read address ["+ bin2hex(address)+"]"

            cmd_to_cache.send(instruction)
            data = data_from_cache.recv()
            print "CORE("+str(identity)+"): Read value from L1 CACHE("+str(identity)+"): " + str(data)
        else:
            data = randint(0,255)
            print "\n--------------------------------------------------------------------------------------"
            print "CORE("+str(identity)+"): <I"+str(counter_core+count)+"> Write value ("+str(data)+") to address ["+ bin2hex(address)+"]"

            data_to_cache.send(data)
            cmd_to_cache.send(instruction)
        count+=1
        sleep(1/100.)
        

def core(param_dicc=None, debug=False, core1_sprint=3, core2_sprint=1):
    #Lists of instructions for both cores
    ins_list_core1=param_dicc["instructions_core1"]
    ins_list_core2=param_dicc["instructions_core2"]

    #Interface ports to communicate with L1 cache1 (Python Multiprocessing Pipe)
    cmd_to_cache1=param_dicc["cmd_to_cache1"]
    data_from_cache1=param_dicc["data_from_cache1"]
    data_to_cache1=param_dicc["data_to_cache1"]
    
    
    #Interface ports to communicate with L1 cache2 (Python Multiprocessing Pipe)
    cmd_to_cache2=param_dicc["cmd_to_cache2"]
    data_from_cache2=param_dicc["data_from_cache2"]
    data_to_cache2=param_dicc["data_to_cache2"]

    #Instruction counters for both
    counter_core1=0
    counter_core2=0
    
    sleep(0.5) #Wait for the rest to initialize

    while counter_core1 < len(ins_list_core1) or counter_core2 < len(ins_list_core2):
        
        if counter_core1 < len(ins_list_core1):
            #Execute core1_sprint instructions
            execute_n(ins_list_core1, cmd_to_cache1, data_to_cache1,
                      data_from_cache1, counter_core1, debug, core1_sprint,
                      identity="1")
            counter_core1 += core1_sprint
        if counter_core2 < len(ins_list_core2):
            #Execute core2_sprint instruction
            execute_n(ins_list_core2, cmd_to_cache2, data_to_cache2,
                      data_from_cache2, counter_core2, debug, core2_sprint,
                      identity="2")
            counter_core2 += core2_sprint
        sleep(1/100.)
                
    print "\nFinished execution..."
