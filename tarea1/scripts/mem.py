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

#Main memory class
class Main_memory():
    #Constructor of the class Main_memory
    def __init__(self, ports, debug=False):
        self.mem_data={}
        self.cmd_from_cache=ports["cmd_from_cache"]
        self.data_from_cache=ports["data_from_cache"]
        self.data_to_cache=ports["data_to_cache"]
        self.debug=debug

    #Function that generates a block wrapping 32 random bytes
    def generate_block(self):
        block=[]
        for i in xrange(32):
            block.append(randint(0,255))
        return block

    #Function that stores a block in corresponding memory location
    def store_block(self, address, block):
        self.mem_data[address]=block

    #Function that simulates main memory circuit behavior by an infinite loop
    def execution_loop(self):
        while True:
            [address, command] = self.cmd_from_cache.recv()
            
            if command == "{L}":
                if self.debug: print "MEMORY: Send Block ["+bin2hex(address)+"] to L2 CACHE"
                if address in self.mem_data:
                    self.data_to_cache.send(self.mem_data[address])
                else:
                    block = self.generate_block()
                    self.store_block(address, block)
                    self.data_to_cache.send(block)
            else:
                if self.debug: print "MEMORY: Receive Block ["+bin2hex(address)+"] from L2 CACHE"
                self.store_block(address, self.data_from_cache.recv())
                    
#Function to be run by main memory process
def mem(ports, debug):
    memory=Main_memory(ports, debug)
    memory.execution_loop()
