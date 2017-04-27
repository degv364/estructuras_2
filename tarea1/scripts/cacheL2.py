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
from block import Block_MVI


#One way L2 cache class, applies regular Write-back approach to blocks (not MESI)
class Cache1w():
    #Constructor of the class Cache1w, data size in bytes, block size in bytes
    def __init__(self, data_size, block_size, ports={}, debug=False):
        self.debug=debug
        #Interface ports to communicate with L1 cache (Python Multiprocessing Pipe)
        self.cmd_from_cache=ports["cmd_from_cache"]
        self.data_from_cache=ports["data_from_cache"]
        self.data_to_cache=ports["data_to_cache"]
        
        #Interface ports to communicate with main memory (Python Multiprocessing Pipe)
        self.cmd_to_mem=ports["cmd_to_mem"]
        self.data_from_mem=ports["data_from_mem"]
        self.data_to_mem=ports["data_to_mem"]
        
        #Amount of blocks in L2 cache
        index_size=data_size/block_size;

        #Index width of bits in address
        self.index_width=int(ceil(log2(index_size)));

        #Offset width of bits in address
        self.offset_width=int(ceil(log2(block_size)))

        #Dictionary that contains the blocks
        self.data={}

        #Instruction given by L1 cache
        self.instruction=None

        #Fill data dictionary with blocks
        for index in xrange(index_size):
            self.data[int2bin(index, self.index_width)]=Block_MVI()


    #Function that splits the address given by cache instruction in tag, index and offset    
    def split_address(self):
        #instruction is a list, first element is address
        address = self.instruction[0]
        offset = address[-self.offset_width:]
        index = address[(-self.index_width-self.offset_width):-self.offset_width]
        tag = address[:(-self.index_width-self.offset_width)]
        return [tag, index, offset] #return a list with tag, index and offset

    
    #Function that executes the instruction given by the L1 cache
    def run_instruction(self):
        #Using pipe port to get core instruction
        self.instruction = self.cmd_from_cache.recv()
        command = self.instruction[1]
        [tag, index, offset] = self.split_address()

        #Gets a reference to the corresponding index block
        my_block = self.data[index]

        #Handle miss condition
        if tag != my_block.tag or my_block.state == "i": 
            if self.debug: print "L2 CACHE miss "+ bin2hex(tag+index+offset)
            self.handle_miss(index, tag, offset)
            
            
        #Execute operation as determined by command (read or write)
        if command=="{L}":
            if self.debug: print "L2 CACHE send to L1 "+ bin2hex(tag+index+offset)
            self.cache_read(my_block)
            
        else:
            if self.debug: print "L2 CACHE recv from L1 "+ bin2hex(tag+index+offset)
            data = self.data_from_cache.recv()
            self.cache_write(my_block, data)
            

            
    #Function that handles a miss condition, fetching block from main memory
    def handle_miss(self, index, tag, offset):
        #Get local block to be overwritten
        my_block = self.data[index]

        #If my_block is Modified, first flush my_block data to main memory
        if my_block.state == "m": self.flush(index, my_block.tag, offset, my_block.data)

        #Block state transition to valid
        my_block.state = "v"

        #Update my_block tag
        my_block.tag = tag 
        #Finally copy data from main memory
        my_block.data = self.fetch(index, tag, offset)
        

    #Function that reads requested data and sends it to L1 cache (after miss handling)
    def cache_read(self, my_block):
        #Send data requested by L1 cache
        self.data_to_cache.send(my_block.data)

        
    #Function that writes requested data from L1 cache (after miss handling)
    def cache_write(self, my_block, data):
        #Impossible to have invalid. If modified -> no state change
        if my_block.state == "v": my_block.state == "m"
        #Receive whole block from L1 cache
        my_block.data = data

        
    #Function that reads required block from main memory
    def fetch(self, index, tag, offset):
        if self.debug: print "L2 CACHE fetching from mem "+ bin2hex(tag+index+offset)
        #Assemble a read request for main memory
        mem_request = [tag+index+offset, "{L}"]
        #Send request to main memory
        self.cmd_to_mem.send(mem_request)
        #Returns data received from main memory
        return self.data_from_mem.recv()


    #Function that writes dirty block to main memory 
    def flush(self, index, tag, offset, data):
        if self.debug: print "L2 CACHE flushing to mem"+ bin2hex(tag+index+offset)
        #Assemble a write request for main memory
        mem_request = [tag+index+offset, "{S}"]
        #Send data to be written in main memory
        self.data_to_mem.send(data)
        #Send request to main memory
        self.cmd_to_mem.send(mem_request)

        
    #Function that simulates L2 cache circuit behavior by an infinite loop
    def execution_loop(self):
        while (True):
            if not self.cmd_from_cache.poll():
                sleep(1/1000.)
            else:
                #There is a command from L1 cache
                self.run_instruction()

#Function to be run by L2 cache process
def cacheL2(ports, debug):
    #Instantiation of L2 cache module
    cache=Cache1w(128*1024, 32, ports, debug)
    cache.execution_loop() 
