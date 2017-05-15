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
    def __init__(self, ports, debug=False, print_queue=None, sig_kill=None):
        self.mem_data={}
        self.cmd_from_cache=ports["cmd_from_cache"]
        self.data_from_cache=ports["data_from_cache"]
        self.data_to_cache=ports["data_to_cache"]

        self.print_queue=print_queue
        self.debug=debug
        self.sig_kill=sig_kill
        

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
        while (not self.sig_kill.poll()):
            if self.cmd_from_cache.poll():
                [address, command] = self.cmd_from_cache.recv()
                
                if command == "{L}":
                    debug_print("MEMORY: Send Block ["+bin2hex(address)+"] to L2 CACHE",
                                self.print_queue, self.debug)

                    if address in self.mem_data:
                        self.data_to_cache.send(self.mem_data[address])
                    else:
                        block = self.generate_block()
                        self.store_block(address, block)
                        self.data_to_cache.send(block)
                else:
                    debug_print("MEMORY: Receive Block ["+bin2hex(address)+"] from L2 CACHE",
                                self.print_queue, self.debug)

                    self.store_block(address, self.data_from_cache.recv())
            sleep(1/100.)
                    
#Function to be run by main memory process
def mem(ports=None, debug=False, print_queue=None, sig_kill=None):
    memory = Main_memory(ports, debug, print_queue, sig_kill)
    memory.execution_loop()
    
