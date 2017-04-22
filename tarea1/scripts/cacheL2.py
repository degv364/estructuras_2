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
from block import Block_MVI



class Cache1w():
    # data size and block size in bytes. 
    def __init__(self, data_size, block_size,param_dicc={}, debug=False):
        self.debug=debug
        self.cmd_from_cache=param_dicc["cmd_from_cache"]
        self.data_from_cache=param_dicc["data_from_cache"]
        self.data_from_mem=param_dicc["data_from_mem"]
        self.cmd_to_mem=param_dicc["cmd_to_mem"]
        self.data_to_mem=param_dicc["data_to_mem"]
        self.data_to_cache=param_dicc["data_to_cache"]
        
        index_cant=data_size/block_size;
        self.index_size=int(log2(index_cant));
        self.offset_size=int(log2(block_size))
        self.data={}
        self.instruction=None
        for index in xrange(index_cant):
            self.data[int2bin(index, self.index_size)]=Block_MVI()

    def split_instruction(self, ins):
        #instruction is a list, first element is address, return a list with tag, index and offset
        
        address=ins[0]
        offset=ins[-self.offset_size:]
        index=ins[(-self.index_size-self.offset_size):-self.offset_size]
        tag=ins[:(-self.index_size-self.offset_size)]
        return [tag,index,offset]

    def run_instruction(self, instruction=None, data=None):
        self.instruction=instruction
        command=instruction[1]
        [tag, index, offset]=self.split_instruction(instruction)
        my_block=self.data[index]
        
        if tag!=my_block.n_tag or my_block.n_state=="i": #Miss, invalid in case tag==0
            self.handle_miss(tag, index, offset)
        if command=="{L}":
            self.cache_read(tag, index, offset)
        else:
            self.cache_write(tag, index, offset, data)

    def cache_read(self, tag, index, offset):
        if self.debug: print "CACHEL2 send to L1 "+tag+index+offset
        my_block=self.data[index]
        self.data_to_cache.send(my_block.n_data)#send whole block data

    def cache_write(self, tag, index, offset):
        if self.debug: print "CACHEL2 recv from L1 "+tag+index+offset
        my_block=self.data[index]
        if my_block.n_state=="v": #impossible to have invalid. if modified -> no state change
            my_block.n_state=="m"
        my_block.n_data=self.data_from_cache.recv()#cahceL1 sent whole block data
            
    def handle_miss(self, tag, index, offset):
        if self.debug: print "CACHEL2 miss "+tag+index+offset
        my_block=self.data[index]
        if my_block.n_state=="m":
            self.flush(tag, index, offset)
        my_block.n_data=self.fetch_from_memory(tag, index, offset)
        my_block.n_state="v"
        
    
    def fetch_from_memory(self, tag, index, offset):
        if self.debug: print "CACHEL2 fecthing from mem "+tag+index+offset
        ins=[tag+index+offset, "{L}"]
        self.cmd_to_mem.send(ins)
        return self.data_from_mem.recv()
    
    def flush(self, tag, index, offset): #FIXME: Check when to flush 
        #generate a write instruction for memory
        if self.debug: print "CACHEL2 flushing "+tag+index+offset
        ins=[tag+index+offset, "{S}"]
        my_block=self.data[index]
        data=my_block.n_data
        self.data_to_mem.send(data)
        self.cmd_to_mem.send(ins)

    def execution_loop(self):
        while (True):
            if not self.cmd_from_cache.poll():
                sleep(1/1000)
            else:
                #there is a command from cacheL1
                instruction=self.cmd_from_cache.recv()
                if self.data_from_cache.poll()
                    data=self.data_from_cache.recv()
                else:
                    data=None
                self.run_instruction(instruction, data) #FIXME: change implementation

def cacheL2(param_dicc, debug):
    cache=Cache1w(128000, 32,param_dicc, debug)
    cache.execution_loop() 
