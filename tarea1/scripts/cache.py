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
from utils import log2, log16, int2hex, int2bin, hex2bin, hex2bin, bin2hex




 class Block1w():
    #one way block
    def __init__(self, state="i", tag=None, info=None):
        #info is a list with every byte
        self.state=state #four possible values: m, e, s, i
        self.tag=tag
        self.info=info
    def reset(self):
        self.state="i"

    def request(offset):
        #return the 4 bytes of the word in offset
        data=[0,0,0,0]
        for i in [0,1,2,3]:
            data[i]=self.info[int(offset,2)+i]
        return data #return a copy of the object, in ython evetything is a reference
        
    def write_on(offset, data):
        #data is a list with 4 bytes
        for i in [0,1,2,3]:
            self.info[int(offset, 2)+i]=data[i]

class Cache1w():
    #data sizr in bytes, block size in bytes, asociativity is a bool
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
            self.data[int2bin(index, self.index_size)]=Block1w()

    def split_instruction(self, instruction):
        #instruction is a list, fisrt element is adress, return a list with tag, index and offset
        #instruction coems in hex
        address=instruction[0]
        ins=hex2bin(address.split('x')[1])
        offset=ins[-self.offset_size:]
        index=ins[(-self.index_size-self.offset_size):-self.offset_size]
        tag=ins[:(-self.index_size-self.offset_size)]
        return [tag,index,offset]


    def execution_loop(self):
        while (True):
            if not (self.cmd_from_cache.poll():
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

    


def cacheL1(param_dicc):
    #FIXME: missing implementation
    pass
    

