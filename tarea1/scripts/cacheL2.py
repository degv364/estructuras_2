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
    #data size in bytes, block size in bytes, asociativity is a bool
    #note that there is no need for shared, since this cache is alone
    #bus side requests, onlyflush has effect, the rest depend on havin more than one cache
    def __init__(self, data_size, block_size,param_dicc={}):

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

    def split_instruction(self, instruction):
        #instruction is a list, first element is address, return a list with tag, index and offset
        #instruction comes in hex
        address=instruction[0]
        ins=hex2bin(address.split('x')[1])
        offset=ins[-self.offset_size:]
        index=ins[(-self.index_size-self.offset_size):-self.offset_size]
        tag=ins[:(-self.index_size-self.offset_size)]
        return [tag,index,offset]

    def run_instruction(self, instruction, data):
        self.instruction=instruction
        command=instruction[1]
        [tag, index, offset]=self.split_instruction(instruction)
        my_block=self.data[index]
        
        if tag!=my_block.tag: #Miss
            self.handle_miss() #FIXME: missing implementation
        if command=="{L}":
            self.cache_read(tag, index, offset)
        else:
            self.cache_write(tag, index, offset, data)

    def cache_read(self, tag, index, offset):
        my_block=self.data[index]
        self.data_to_cache.send(my_block.data)

    def cache_write(self, tag, index, offset):
        my_block=self.data[index]
        

    def fetch_from_memory(self, tag, index, offset):
        self.cmd_to_mem.send(self.instruction)
        return self.data_from_mem.recv()

    
    def flush(self, tag, index, offset): #FIXME: Check when to flush 
        #generate a write instruction for memory
        ins=[tag+index+offset, "{S}"]
        my_block=self.data[index]
        data=my_block.data
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



def cacheL2(param_dicc):
    cache=Cache1w(128000, 32,param_dicc)
    cache.execution_loop() 
