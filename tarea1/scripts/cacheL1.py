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
from block import Block #FIXME: maybe another file

#this calss will control the "recent of use"
class Block_pair():
    def __init__(self, block1, block2):
        self.recent=block1
        self.not_r=block2

    def get_lru(self):
        #this will be used in case of miss
        return self.not_r

    def get_by_tag(self, tag):
        #FIXME:change this implementation to use block methods
        if self.recent.tag==tag and self.recent.state!="i":
            return self.recent
        elif self.not_r.tag==tag and self.not_r.state!="i":
            #not_r has been used, so must be recent, make swap
            temp=self.not_r
            self.not_r=self.recent
            self.recent=temp
            return self.recent
        else:
            #none has the tag or all are invalid, then is a miss
            return None

    def bus_need_tag(self, tag):
        #returns a block but needed by bus, then recent is not updated
        if self.recent.tag==tag:
            return self.recent
        elif self.not_r.tag==tag:
            return self.not_r
        else:
            return None
            
        
        

class Cache2w():
    #data sizr in bytes, block size in bytes, asociativity is a bool
    def __init__(self, data_size, block_size,param_dicc={}):
        #cache interacts via ports only with core
        self.cmd_from_core=param_dicc["cmd_from_core"]
        self.data_from_core=param_dicc["data_from_core"]
        self.data_to_core=param_dicc["data_to_core"]

        self.cmd_to_cache=param_dicc["cmd_to_cache"]
        self.data_from_cache=param_dicc["data_from_cache"]
        self.data_to_cache=param_dicc["data_to_cache"]
        
        index_cant=data_size/block_size; #for one way
        index_cant=index_cant/2#for 2 way associative
        self.index_size=int(log2(index_cant));
        self.offset_size=int(log2(block_size))
        self.data={}
        self.instruction=None
        for index in xrange(index_cant):
            self.data[int2bin(index, self.index_size)]=Block_pair(Block(), Block())

    def set_cache(self, cache):
        self.other=cache

    def split_instruction(self):
        #instruction is a list, fisrt element is adress, return a list with tag, index and offset
        #instruction coems in hex
        address=self.instruction[0]
        ins=hex2bin(address.split('x')[1])
        offset=ins[-self.offset_size:]
        index=ins[(-self.index_size-self.offset_size):-self.offset_size]
        tag=ins[:(-self.index_size-self.offset_size)]
        return [tag,index,offset]

    def run_instruction(self):
        self.instruction=self.cmd_from_core.recv()
        command=self.instruction[1]
        [tag, index, offset]=self.split_instruction()
        block_pair=self.data[index]
        my_block=block_pair.get_by_tag(tag)
        if not my_block:
            #will enter here in case of a miss
            my_block=block_pair.get_lru()
            #invalidate my_block
        if command=="{L}":
            self.core_read(tag, index, offset, my_block)
        else:
            data=self.data_from_core.recv()
            self.core_write(tag, index, offset, my_block, data)

    def core_read(tag, index, offset, block):
        #FIXME: missing implementation
        pass
    
    def core_write(tag, index, offset, block, data):
        #FIXME: missing implementation
        pass

    def run_command_from_bus(self):
        #FIXME: missing implementation
        pass





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
                #command is from core2
                cache2.run_instruction()





def cacheL1(param_dicc):
    #FIXME: prepare param diccionaries for the caches
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
    cache1.set_cache(cache2) #not possibel in the constructor, becasue it does not exist
    cache2.set_cache(cache1)
    execution_loop(cache1, cache2, param_dicc) 
