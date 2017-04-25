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

#Two way associative L1 cache class, applies MESI protocol to blocks
class Cache2w():

    #Constructor of the class Cache2w, data size in bytes, block size in bytes
    def __init__(self, data_size, block_size,param_dicc={}):
        #Interface ports to communicate with local core (Python Multiprocessing Pipe)
        self.cmd_from_core=param_dicc["cmd_from_core"]
        self.data_from_core=param_dicc["data_from_core"]
        self.data_to_core=param_dicc["data_to_core"]

        #Interface ports to communicate with L2 cache (Python Multiprocessing Pipe)
        self.cmd_to_cache=param_dicc["cmd_to_cache"]
        self.data_from_cache=param_dicc["data_from_cache"]
        self.data_to_cache=param_dicc["data_to_cache"]

        #Amount of sets in L1 cache
        index_size=data_size/block_size; #Number of ways
        index_size=index_size/2 #Number of sets (2 way associative)

        #Index width of bits in address
        self.index_width=int(log2(index_size));

        #Offset width of bits address
        self.offset_width=int(log2(block_size))

        #Dictionary that contains the block pairs (sets)
        self.data={}

        #Instruction given by core
        self.instruction=None

        #Fill data dictionary with block pairs (sets)
        for index in xrange(index_size):
            self.data[int2bin(index, self.index_width)]=Block_pair(Block_MESI(), Block_MESI())


    #Function that sets a reference to the other L1 cache in the bus (as there are only two L1 caches)        
    def set_cache(self, cache):
        self.other=cache


    #Function that splits the address given by core instruction in tag, index and offset
    def split_instruction(self):
        address = self.instruction[0]
        offset = address[-self.offset_width:]
        index = address[(-self.index_width-self.offset_width):-self.offset_width]
        tag = address[:(-self.index_width-self.offset_width)]
        return [tag, index, offset] #return a list with tag, index and offset


    #Function that executes the instruction given by the core
    def run_instruction(self):
        #Using Pipe port to get core instruction
        self.instruction = self.cmd_from_core.recv() 
        command = self.instruction[1]
        [tag, index, offset] = self.split_instruction()

        #Gets a reference to the corresponding set (as determined by index)
        my_block_pair = self.data[index]

        #If my_block is None indicates a miss, else it means the block was found (as determined by tag)
        my_block = my_block_pair.get_by_tag(tag) 

        #Handle miss condition
        if my_block == None:
            self.handle_miss(index, tag, my_block_pair)
            #Fetch block again, now that it is there
            my_block = my_block_pair.get_by_tag(tag) 
            
        #Execute operation, as determined by command (read or write)
        if command=="{L}": 
            self.core_read(my_block, offset)
        else:
            data = self.data_from_core.recv()
            self.core_write(my_block, offset, data)


    #Function that handles a miss condition, fetching block from other L1 cache or L2 cache
    def handle_miss(index, tag, block_pair):
        #Get local block to be overwritten by LRU policy
        my_block = block_pair.get_lru()
        #Look for block in the other L1 cache (bus)
        other_block = self.other.bus_search_block(index, tag) 
        
        if other_block is not None: #Block found in other L1
            #Change my_block state if necessary
            my_flush = my_block.fsm_transition("Miss", True) 
            #If my_block is Modified, first flush my_block data to L2
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Change other_block state if necessary (BusRd signal)
            other_flush = other_block.fsm_transition("BusRd")
            #If other_block is Modified, first flush other_block data to L2
            if other_flush == True: self.flush(index, other_block.tag, other_block.data)

            #Finally copy data from other block
            my_block.data = other_block.data 

        else:  #Should fetch block from L2 cache
            #Change my_block state if necessary
            my_flush = my_block.fsm_transition("Miss", True)
            #If my_block is Modified, first flush my_block data to L2
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Finally copy data from L2 cache
            my_block.data = self.fetch(index, my_block.tag)
            

    #Function that reads requested data (one byte) and sends it to core (after miss handling)
    def core_read(self, my_block, offset):
        data = my_block.read(offset) #Get requested byte from block
        my_block.fsm_transition("PrRd")
        #Using Pipe port to give data to core
        self.data_to_core.send(data)


    #Function that writes requested data (one byte) (after miss handling)
    def core_write(self, my_block, index, offset, data):
        #If line is shared first try to invalidate other L1 cache line
        if block.state == "s": 
            other_block = self.other.bus_search_block(index, my_block.tag)
            #As established by MESI, in Shared state, block may or may not be in other L1, so check if not None
            if other_block is not None:
                other_block.fsm_transition("BusRdX") #Invalidate other line

        #Change my_block state if necessary
        block.fsm_transition("PrWr")
        #Write data to block
        block.write(offset, data)

        
    #Function that reads required block from L2 cache
    def fetch(self, index, tag):
        #Assemble a read request to L2 cache
        cache_request = [tag+index+("0"*self.offset_width), "{L}"] 
        #Send request to L2 cache
        self.cmd_to_cache.send(cache_request)
        #Returns data received from L2 cache
        return self.data_from_cache.recv()

    
    #Function that writes required block to L2 cache 
    def flush(self, index, tag, data):
        #Send data to be written in L2 cache
        self.data_to_cache.send(data)
        #Assemble a write request to L2 cache
        cache_request = [tag+index+("0"*self.offset_width), "{S}"]
        #Send request to L2 cache
        self.cmd_to_cache.send(cache_request)


    #Function used by other L1 cache to search a block
    def bus_search_block(self, index, tag):
        block_pair = self.data[index]
        #False makes get request not affect LRU counters (bus read)
        my_block = block_pair.get_by_tag(tag, False)
        return my_block


#Function that simulates cache L1 circuit behavior establishing an infinite loop
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


#Function to be run by cache L1 process (includes both L1 caches)
def cacheL1(param_dicc):
    #cache1 interface pipe ports
    param_dicc1["cmd_from_core"]=param_dicc["cmd_from_core1"]
    param_dicc1["data_from_core"]=param_dicc["data_from_core1"]
    param_dicc1["data_to_core"]=param_dicc["data_to_core1"]

    param_dicc1["cmd_to_cache"]=param_dicc["cmd_to_cache"]
    param_dicc1["data_from_cache"]=param_dicc["data_from_cache"]
    param_dicc1["data_to_cache"]=param_dicc["data_to_cache"]
    
    #cache2 interface pipe ports
    param_dicc2["cmd_from_core"]=param_dicc["cmd_from_core2"]
    param_dicc2["data_from_core"]=param_dicc["data_from_core2"]
    param_dicc2["data_to_core"]=param_dicc["data_to_core2"]
    
    param_dicc2["cmd_to_cache"]=param_dicc["cmd_to_cache"]
    param_dicc2["data_from_cache"]=param_dicc["data_from_cache"]
    param_dicc2["data_to_cache"]=param_dicc["data_to_cache"]

    #Instantiation of both L1 cache modules
    cache1=Cache2w(16000, 32, param_dicc1)
    cache2=Cache2w(16000, 32, param_dicc2)
    #Set other L1 cache reference for both L1 cache modules, not possible in the constructor
    cache1.set_cache(cache2)
    cache2.set_cache(cache1)
    
    #Run execution loop
    execution_loop(cache1, cache2, param_dicc) 
