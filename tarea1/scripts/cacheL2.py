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
    def __init__(self, data_size, block_size, ports={}, debug=False, print_queue=None):
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

        self.print_queue=print_queue
        self.debug=debug

        #Miss counting variables
        self.miss=0.
        self.total_instructions=0.
            
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
        self.total_instructions+=1
        #Using pipe port to get core instruction
        self.instruction = self.cmd_from_cache.recv()
        command = self.instruction[1]
        operation = "Read" if command=="{L}" else "Write"
        [tag, index, offset] = self.split_address()

        #Gets a reference to the corresponding index block
        my_block = self.data[index]

        miss_flag = (tag != my_block.tag) or (my_block.state == "i")
        

        #Handle miss condition
        if miss_flag: 
            debug_print("L2 CACHE: "+operation+" MISS for Block ["+ bin2hex(tag+index+offset)+"]",
                        self.print_queue, self.debug)
            self.handle_miss(index, tag, offset)
        else:
            debug_print("L2 CACHE: "+operation+" HIT for Block ["+ bin2hex(tag+index+offset)+"]",
                        self.print_queue, self.debug)
            
        #Execute operation as determined by command (read or write)
        if command=="{L}":
            debug_print("L2 CACHE: Send Block ["+ bin2hex(tag+index+offset)+"] to L1 CACHE",
                        self.print_queue, self.debug)
            self.cache_read(index, my_block)
        else:
            debug_print("L2 CACHE: Receive Block ["+ bin2hex(tag+index+offset)+"] from L1 CACHE",
                        self.print_queue, self.debug)

            data = self.data_from_cache.recv()
            self.cache_write(index, my_block, data)
            

            
    #Function that handles a miss condition, fetching block from main memory
    def handle_miss(self, index, tag, offset):
        self.miss+=1
        #Get local block to be overwritten
        my_block = self.data[index]
        flush_flag = my_block.state == "m"

        #If my_block is Modified, first flush my_block data to main memory
        if flush_flag: self.flush(index, my_block.tag, offset, my_block.data)
        
        #Block state transition to valid
        initial_state = my_block.state
        final_state = my_block.state = "v"
        self.print_fsm_transition("Miss", int(index,2), initial_state, final_state, flush_flag)

        #Update my_block tag
        my_block.tag = tag 
        #Finally copy data from main memory
        my_block.data = self.fetch(index, tag, offset)
        

    #Function that reads requested data and sends it to L1 cache (after miss handling)
    def cache_read(self, index, my_block):
        final_state = initial_state = my_block.state
        self.print_fsm_transition("Read", int(index,2), initial_state, final_state, flush=False)

        #Send data requested by L1 cache
        self.data_to_cache.send(my_block.data)

        
    #Function that writes requested data from L1 cache (after miss handling)
    def cache_write(self, index, my_block, data):
        #Impossible to have invalid. If modified => no state change
        initial_state = my_block.state
        if my_block.state == "v": my_block.state = "m"
        final_state = my_block.state
        self.print_fsm_transition("Write", int(index,2), initial_state, final_state, flush=False)
            
        #Receive whole block from L1 cache
        my_block.data = data

        
    #Function that reads required block from main memory
    def fetch(self, index, tag, offset):
        debug_print("L2 CACHE: Fetch Block ["+bin2hex(tag+index+offset)+"] from Main Memory",
                    self.print_queue, self.debug)
            
        #Assemble a read request for main memory
        mem_request = [tag+index+offset, "{L}"]
        #Send request to main memory
        self.cmd_to_mem.send(mem_request)
        #Returns data received from main memory
        return self.data_from_mem.recv()


    #Function that writes dirty block to main memory 
    def flush(self, index, tag, offset, data):
        debug_print("L2 CACHE: Flush Block ["+bin2hex(tag+index+offset)+"] to Main Memory",
                    self.print_queue, self.debug)

        #Assemble a write request for main memory
        mem_request = [tag+index+offset, "{S}"]
        #Send data to be written in main memory
        self.data_to_mem.send(data)
        #Send request to main memory
        self.cmd_to_mem.send(mem_request)


    def print_fsm_transition(self, request, index, initial_state, final_state, flush):
        print_msg = "L2 CACHE: Block Index ["+str(index)+"] FSM:\n"
        print_msg += "--------- Request <"+request+">: --Initial State: {"+initial_state.upper()+"} "
        print_msg += "--Final State: {"+final_state.upper()+"} --Flush: ("+("Yes" if flush else "No")+")"
        self.print_queue.put(print_msg)

        
    #Function that simulates L2 cache circuit behavior by an infinite loop
    def execution_loop(self, sig_kill=None):
        while (not sig_kill.poll()):
            if not self.cmd_from_cache.poll():
                sleep(1/1000.)
            else:
                #There is a command from L1 cache
                self.run_instruction()
    def final_state(self):
        #return all variables required for final state
        f_state={"Misses":self.miss,
                 "Total_instructions": self.total_instructions,
                 "Miss_rate":round(self.miss/self.total_instructions, 3)}

        f_state["Hit_rate"]=round(1-f_state["Miss_rate"], 3)
        

        return f_state
    def formated_final_state_text(self):
        f=self.final_state()
        text="+--+--"*15+"\n|L2 CACHE Final Statistics:"
        text+="\n| -> Miss Rate: "+str(f["Miss_rate"])
        text+="\n| -> Hit Rate: "+str(f["Hit_rate"])
        text+="\n"+"+--+--"*15
        return text

#Function to be run by L2 cache process
def cacheL2(ports, debug, print_queue, sig_kill=None, last_state_port=None):
    #Instantiation of L2 cache module
    cache=Cache1w(128*1024, 32, ports, debug, print_queue)
    cache.execution_loop(sig_kill)
    last_state_port.send(cache.final_state())
    debug_print(cache.formated_final_state_text(), print_queue, debug)
    
