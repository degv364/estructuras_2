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
from block import Block_MESI, Block_pair

#Two way associative L1 cache class, applies MESI protocol to blocks
class Cache2w():

    #Constructor of the class Cache2w, data size in bytes, block size in bytes
    def __init__(self, data_size, block_size, ports={}, debug=False, iden=None, print_queue=None):
        #Interface ports to communicate with local core (Python Multiprocessing Pipe)
        self.cmd_from_core=ports["cmd_from_core"]
        self.data_from_core=ports["data_from_core"]
        self.data_to_core=ports["data_to_core"]

        #Interface ports to communicate with L2 cache (Python Multiprocessing Pipe)
        self.cmd_to_cache=ports["cmd_to_cache"]
        self.data_from_cache=ports["data_from_cache"]
        self.data_to_cache=ports["data_to_cache"]

        #Amount of sets in L1 cache
        index_size=data_size/block_size; #Number of ways
        index_size=index_size/2 #Number of sets (2 way associative)

        #Index width of bits in address
        self.index_width=int(ceil(log2(index_size)));

        #Offset width of bits in address
        self.offset_width=int(ceil(log2(block_size)))
        
        #Dictionary that contains the block pairs (sets)
        self.data={}

        #Instruction given by core
        self.instruction=None

        #Fill data dictionary with block pairs (sets)
        for index in xrange(index_size):
            self.data[int2bin(index, self.index_width)]=Block_pair(Block_MESI(n_setid = 1),
                                                                   Block_MESI(n_setid = 2))

        self.print_queue = print_queue
        #Debug flags
        self.debug = debug
        self.iden=iden #identity for debug messages


    #Function that sets a reference to the other L1 cache in the bus (only two L1 caches)
    def set_cache(self, cache):
        self.other=cache


    #Function that splits the address given by core instruction in tag, index and offset
    def split_address(self):
        #instruction is a list, first element is address
        address = self.instruction[0]
        offset = address[-self.offset_width:]
        index = address[(-self.index_width-self.offset_width):-self.offset_width]
        tag = address[:(-self.index_width-self.offset_width)]
        return [tag, index, offset] #return a list with tag, index and offset


    #Function that executes the instruction given by the core
    def run_instruction(self):
        #Using pipe port to get core instruction
        self.instruction = self.cmd_from_core.recv() 
        command = self.instruction[1]
        [tag, index, offset] = self.split_address()

        #Gets a reference to the corresponding index set
        my_block_pair = self.data[index]
        
        #If my_block is None indicates a miss, else it means the block was found by tag
        my_block = my_block_pair.get_by_tag(tag) 

        miss_flag = my_block == None
        
        #Handle miss condition
        if miss_flag:
            if self.debug:
                print_msg = "L1 CACHE("+self.iden+"): MISS for address ["+ bin2hex(tag+index+offset)+"]"
                self.print_queue.put(print_msg)
                
            self.handle_miss(index, tag, my_block_pair)
            #Fetch block again, now that it is there
            my_block = my_block_pair.get_by_tag(tag) 
            
        if self.debug and not miss_flag:
            print_msg = "L1 CACHE("+self.iden+"): HIT for address ["+ bin2hex(tag+index+offset)+"]"
            self.print_queue.put(print_msg)
            
        #Execute operation as determined by command (read or write)
        if command=="{L}":
            if self.debug:
                print_msg = "L1 CACHE("+self.iden+"): Send Data ["+ bin2hex(tag+index+offset)+"] to CORE("+self.iden+")"
                self.print_queue.put(print_msg)

            self.core_read(my_block, index, offset)
        else:
            if self.debug:
                print_msg = "L1 CACHE("+self.iden+"): Receive Data ["+bin2hex(tag+index+offset)+"] from CORE("+self.iden+")"
                self.print_queue.put(print_msg)

            data = self.data_from_core.recv()
            self.core_write(my_block, index, offset, data)


    #Function that handles a miss condition, fetching block from other L1 cache or L2 cache
    def handle_miss(self, index, tag, block_pair):
        #Get local block to be overwritten by LRU policy
        my_block = block_pair.get_lru()
        #Look for block in the other L1 cache (bus)
        other_block = self.other.bus_search_block(index, tag) 
        
        if other_block is not None: #Block found in other L1
            if self.debug:
                print_msg = "L1 CACHE("+self.iden+"): Bus Reply: Missing Block found in L1 CACHE("+self.other.iden+")"
                self.print_queue.put(print_msg)
                
            #Change my_block state if necessary
            my_request = "Miss"
            my_initial = my_block.state
            my_flush = my_block.fsm_transition(my_request, True) 
            my_final = my_block.state
            self.debug_fsm_transition(my_request, my_block.setid, int(index,2), my_initial, my_final, my_flush)
            
            #If my_block is Modified, first flush my_block data to L2
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Change other_block state if necessary (BusRd signal)
            other_request = "BusRd"
            other_initial = other_block.state
            other_flush = other_block.fsm_transition(other_request)
            other_final = other_block.state
            self.other.debug_fsm_transition(other_request, other_block.setid, int(index,2), other_initial, other_final, other_flush)
            
            #If other_block is Modified, first flush other_block data to L2
            if other_flush == True: self.flush(index, other_block.tag, other_block.data)

            #Update my_block tag
            my_block.tag = tag 
            #Finally copy data from other block
            my_block.data = other_block.data 

        else:  #Should fetch block from L2 cache
            if self.debug:
                print_msg = "L1 CACHE("+self.iden+"): Bus Reply: Missing Block NOT found in L1 CACHE("+self.other.iden+")"
                self.print_queue.put(print_msg)

            #Change my_block state if necessary
            my_request = "Miss"
            my_initial = my_block.state
            my_flush = my_block.fsm_transition(my_request)
            my_final = my_block.state
            self.debug_fsm_transition(my_request, my_block.setid, int(index,2), my_initial, my_final, my_flush)

            #If my_block is Modified, first flush my_block data to L2
            if my_flush == True: self.flush(index, my_block.tag, my_block.data)

            #Update my_block tag
            my_block.tag = tag
            #Finally copy data from L2 cache
            my_block.data = self.fetch(index, my_block.tag)
            

    #Function that reads requested data (one byte) and sends it to core (after miss handling)
    def core_read(self, my_block, index, offset):
        #Get requested byte from block
        data = my_block.read(offset)
        my_request = "PrRd"
        my_initial = my_block.state
        my_block.fsm_transition(my_request)
        my_final = my_block.state
        self.debug_fsm_transition(my_request, my_block.setid, int(index,2), my_initial, my_final, False)
        #Using pipe port to give data to core
        self.data_to_core.send(data)


    #Function that writes requested data (one byte) (after miss handling)
    def core_write(self, my_block, index, offset, data):
        #If line is shared first try to invalidate other L1 cache line
        if my_block.state == "s": 
            other_block = self.other.bus_search_block(index, my_block.tag)
            #In MESI state 'S', block may or may not be in other L1, so check if not None
            if other_block is not None:
                other_request = "BusRdX"
                other_initial = other_block.state
                other_block.fsm_transition(other_request) #Invalidate other line
                other_final = other_block.state
                self.other.debug_fsm_transition("Invalidate", other_block.setid, int(index,2), other_initial, other_final, False)
                
        if self.debug:
            print_msg = "L1 CACHE("+self.iden+"): Write value from CORE("+self.iden+"): " + str(data)
            self.print_queue.put(print_msg)
            
        #Change my_block state if necessary
        my_request = "PrWr"
        my_initial = my_block.state
        my_block.fsm_transition(my_request)
        my_final = my_block.state
        self.debug_fsm_transition(my_request, my_block.setid, int(index,2), my_initial, my_final, False)
        
        #Write data to my_block
        my_block.write(offset, data)

        
    #Function that reads required block from L2 cache
    def fetch(self, index, tag):
        if self.debug:
            print_msg = "L1 CACHE("+self.iden+"): Fetch Block ["+bin2hex(tag+index+("0"*self.offset_width))+"] from L2 CACHE"
            self.print_queue.put(print_msg)

        #Assemble a read request for L2 cache
        cache_request = [tag+index+("0"*self.offset_width), "{L}"] 
        #Send request to L2 cache
        self.cmd_to_cache.send(cache_request)
        #Returns data received from L2 cache
        return self.data_from_cache.recv()

    
    #Function that writes dirty block to L2 cache 
    def flush(self, index, tag, data):
        if self.debug:
            print_msg = "L1 CACHE("+self.iden+"): Flush Block ["+bin2hex(tag+index+("0"*self.offset_width))+"] to L2 CACHE"
            self.print_queue.put(print_msg)

        #Assemble a write request for L2 cache
        cache_request = [tag+index+("0"*self.offset_width), "{S}"]
        #Send data to be written in L2 cache
        self.data_to_cache.send(data)
        #Send request to L2 cache
        self.cmd_to_cache.send(cache_request)


    #Function used by other L1 cache to search a block
    def bus_search_block(self, index, tag):
        if self.debug:
            print_msg = "L1 CACHE("+self.iden+"): Bus Request: Seach for Block ["+bin2hex(tag+index+("0"*self.offset_width))+"]"
            self.print_queue.put(print_msg)

        block_pair = self.data[index]
        #False makes get request not affect LRU counters (bus read)
        my_block = block_pair.get_by_tag(tag, False)
        return my_block


    def debug_fsm_transition(self, request, setid, index, initial_state, final_state, flush):
        print_msg = "L1 CACHE("+self.iden+"): Block in Way ["+str(setid)+"] from Set ["+str(index)+"] FSM:\n"
        print_msg += "------------ Request <"+request+">: --Initial State: {"+initial_state.upper()+"} "
        print_msg += "--Final State: {"+final_state.upper()+"} --Flush: ("+("Yes" if flush else "No")+")"
        self.print_queue.put(print_msg)
        

#Function that simulates L1 cache circuit behavior by an infinite loop
def execution_loop(cache1, cache2, ports):
    while (True):
        if not (ports["cmd_from_core1"].poll() or ports["cmd_from_core2"].poll()):
            sleep(1/1000.)
        else:
            #there is a command from some core
            if ports["cmd_from_core1"].poll():
                #command is from Core 1
                cache1.run_instruction()
            else:
                #command is from Core 2
                cache2.run_instruction()


#Function to be run by L1 cache process (includes both L1 caches)
def cacheL1(ports, debug, print_queue):
    #L1 Cache_1 interface pipe ports
    ports1 = {}
    ports1["cmd_from_core"]=ports["cmd_from_core1"]
    ports1["data_from_core"]=ports["data_from_core1"]
    ports1["data_to_core"]=ports["data_to_core1"]

    ports1["cmd_to_cache"]=ports["cmd_to_cache"]
    ports1["data_from_cache"]=ports["data_from_cache"]
    ports1["data_to_cache"]=ports["data_to_cache"]
    
    #L1 Cache_2 interface pipe ports
    ports2 = {}
    ports2["cmd_from_core"]=ports["cmd_from_core2"]
    ports2["data_from_core"]=ports["data_from_core2"]
    ports2["data_to_core"]=ports["data_to_core2"]
    
    ports2["cmd_to_cache"]=ports["cmd_to_cache"]
    ports2["data_from_cache"]=ports["data_from_cache"]
    ports2["data_to_cache"]=ports["data_to_cache"]

    #Instantiation of both L1 cache modules
    cache1=Cache2w(16*1024, 32, ports1, debug, iden="1", print_queue=print_queue)
    cache2=Cache2w(16*1024, 32, ports2, debug, iden="2", print_queue=print_queue)
    #Set other L1 cache reference for both L1 caches, not possible in the constructor
    cache1.set_cache(cache2)
    cache2.set_cache(cache1)
    
    #Run execution loop
    execution_loop(cache1, cache2, ports) 
