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

class Main_memory():
    def __init__(self, ports, debug=False):
        self.main_dictionary={}
        self.cmd_from_cache=ports["cmd_from_cache"]
        self.data_from_cache=ports["data_from_cache"]
        self.data_to_cache=ports["data_to_cache"]
        self.debug=debug
        
    def generate_block(self):
        block=[]
        for i in xrange(32):
            #generate 32 random bytes
            block.append(randint(0,255))
        return block

    def store_block(self, address, block):
        self.main_dictionary[address]=block
        
    def execution_loop(self):
        while True:
            instruction=cmd_from_cache.recv()
                
            if instruction[1]=="{L}":
                if self.debug: print "MEM: read from "+instruction[0]
                if instruction[0] in main_dictionary:
                    self.data_to_cache.send(main_dictionary[instruction[0]])
                else:
                    block=self.generate_block()
                    self.store_block(instruction[0], block)
                    self.data_to_cache.send(block)
            else:
                if self.debug: print "MEM: write to "+instruction[0]
                self.store_block(instruction[0], self.data_from_cache.recv())
                    

def mem(param_dicc):
    
    memory=Main_memory(param_dicc, debug)
    memory.execution_loop()

    
