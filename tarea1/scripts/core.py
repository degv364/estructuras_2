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


from random import randint
from time import sleep

def execute_3(ins_list_core=[], cmd_to_cache=None, data_to_cache=None, data_from_cache=None, counter_core=0):
    count=0
    while counter_core<=len(ins_list_core) and count<3:
        instruction=ins_list_core[counter_core+count]
        if instruction[1]=="{L}":
            if debug: print "CORE1 read "+instruction[0] 
            cmd_to_cache.send(instruction)
            data=data_from_cache.recv()
        else:
            if debug: print "CORE1 write "+instruction[0] 
            data_to_cache.send(randint(0,255))
            cmd_to_cache.send(instruction)
        count+=1
        

def core(param_dicc, debug):
    ins_list_core1=param_dicc["instructions_core1"]
    cmd_to_cache1=param_dicc["cmd_to_cache1"]
    data_from_cache1=param_dicc["data_from_cache1"]
    data_to_cache1=param_dicc["data_to_cache1"]
    
    
    ins_list_core2=param_dicc["instructions_core2"]
    cmd_to_cache2=param_dicc["cmd_to_cache2"]
    data_from_cache2=param_dicc["data_from_cache2"]
    data_to_cache2=param_dicc["data_to_cache2"]

    counter_core1=0
    counter_core2=0
    
    sleep(0.5)#wait for the rest to initialize

    while counter_core1<=len(ins_list_core1) or counter_core2<=len(ins_list_core2):
        if counter_core1<=len(ins_list_core1):
            #execute 3 instructions
            execute_3(inst_list_core1, cmd_to_cache1, data_to_cache1,
                      data_from_cache1, counter_core1)
            counter_core1+=3
        if counter_core2<=len(ins_list_core2):
            #execute 1 instruction
            instruction=ins_list_core2[counter_core2]
            if instruction[1]=="{L}":
                if debug:  print "CORE2 read "+instruction[0] 
                cmd_to_cache2.send(instruction)
                data=data_from_cache2.recv()
            else:
                if debug: print "CORE1 write "+instruction[0]
                data_to_cache2.send(randint(0,255))
                cmd_to_cache2.send(instruction)

        sleep(1/100)
                
    print "finished execution..."
