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
from utils import *
from block import Block_MESI, Block_pair

        
class Cache2w():
    #data size in bytes, block size in bytes, asociativity is a bool
    def __init__(self, data_size, block_size,param_dicc={}):
        #cache interacts via ports only with core
        self.cmd_from_core=param_dicc["cmd_from_core"]
        self.data_from_core=param_dicc["data_from_core"]
        self.data_to_core=param_dicc["data_to_core"]

        self.cmd_to_cache=param_dicc["cmd_to_cache"]
        self.data_from_cache=param_dicc["data_from_cache"]
        self.data_to_cache=param_dicc["data_to_cache"]
        
        index_cant=data_size/block_size; #for one way
        index_cant=index_cant/2 #for 2 way associative
        self.index_size=int(log2(index_cant));
        self.offset_size=int(log2(block_size))
        self.data={}
        self.instruction=None
        for index in xrange(index_cant):
            self.data[int2bin(index, self.index_size)]=Block_pair(Block_MESI(), Block_MESI())


            
    def set_cache(self, cache):
        self.other=cache


        
    def split_instruction(self):
        ins = self.instruction[0]
        offset = ins[-self.offset_size:]
        index = ins[(-self.index_size-self.offset_size):-self.offset_size]
        tag = ins[:(-self.index_size-self.offset_size)]
        return [tag, index, offset] #return a list with tag, index and offset


    
    def run_instruction(self):
        self.instruction = self.cmd_from_core.recv()
        command = self.instruction[1]
        [tag, index, offset] = self.split_instruction()
        block_pair = self.data[index]
        my_block = block_pair.get_by_tag(tag) #Hit if not None

        #Miss condition
        if my_block == None:
            self.handle_miss(index, tag, block_pair)
            my_block = block_pair.get_by_tag(tag) #Fetch block again
            
        #Execute operation            
        if command=="{L}":
            self.core_read(my_block, offset)
        else:
            data = self.data_from_core.recv()
            self.core_write(my_block, offset, data)


            
    def handle_miss(index, tag, block_pair):
        #copy block from other L1 or L2 cache
        my_block = block_pair.get_lru() #Get block to be overwritten
        other_block = self.other.bus_search_block(index, tag) #Look for block in other L1

        if other_block is not None: #Block found in other L1
            #Flush my_block data to L2
            my_flush = my_block.fsm_transition("Miss", True)
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Flush other_block data to L2
            other_flush = other_block.fsm_transition("BusRd")
            if other_flush == True: self.flush(index, other_block.tag, other_block.data)

            #Copy data from other block
            my_block.data = other_block.data 
        else:
            #Flush my_block data to L2
            my_flush = my_block.fsm_transition("Miss", True)
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Copy data from L2 cache
            my_block.data = self.fetch(index, my_block.tag)
            

            
    def core_read(self, my_block, offset):
        data = my_block.read(offset)
        my_block.fsm_transition("PrRd")
        self.data_to_core.send(data)


        
    def core_write(self, my_block, index, offset, data):
        if block.state == "s": #If line is shared invalidate others
            other_block = self.other.bus_search_block(index, my_block.tag)
            if other_block is not None:
                other_block.fsm_transition("BusRdX") #Invalidate
            
        block.fsm_transition("PrWr")
        block.write(offset, data)

        
        
    def fetch(self, index, tag):
        ins = [tag+index+"00000", "{L}"]
        self.cmd_to_cache.send(ins)
        return self.data_from_cache.recv()

    

    def flush(self, index, tag, data):
        self.data_to_cache.send(data)
        ins = [tag+index+"00000", "{S}"]
        self.cmd_to_cache.send(ins)


        
    def bus_search_block(self, index, tag):
        block_pair = self.data[index]
        my_block = block_pair.get_by_tag(tag, False)
        return my_block



def execution_loop(cache1, cache2, param_dicc):
    while (True):
        if not (param_dicc["cmd_from_core1"].poll() or param_dicc["cmd_from_core2"].poll()):
            sleep(1/1000)
        else:
            #there is a command from some core
            if param_dicc["cmd_from_core1"].poll():
                #command is from core 1
                cache1.run_instruction()
            else:
                #command is from core 2
                cache2.run_instruction()



def cacheL1(param_dicc):
    #cache1
    param_dicc1["cmd_from_core"]=param_dicc["cmd_from_core1"]
    param_dicc1["data_from_core"]=param_dicc["data_from_core1"]
    param_dicc1["data_to_core"]=param_dicc["data_to_core1"]

    param_dicc1["cmd_to_cache"]=param_dicc["cmd_to_cache"]
    param_dicc1["data_from_cache"]=param_dicc["data_from_cache"]
    param_dicc1["data_to_cache"]=param_dicc["data_to_cache"]
    
    #cache2
    param_dicc2["cmd_from_core"]=param_dicc["cmd_from_core2"]
    param_dicc2["data_from_core"]=param_dicc["data_from_core2"]
    param_dicc2["data_to_core"]=param_dicc["data_to_core2"]
    
    param_dicc2["cmd_to_cache"]=param_dicc["cmd_to_cache"]
    param_dicc2["data_from_cache"]=param_dicc["data_from_cache"]
    param_dicc2["data_to_cache"]=param_dicc["data_to_cache"]
    
    cache1=Cache2w(16000, 32, param_dicc1)
    cache2=Cache2w(16000, 32, param_dicc2)
    cache1.set_cache(cache2) #not possible in the constructor, because it does not exist
    cache2.set_cache(cache1)
    execution_loop(cache1, cache2, param_dicc) 
