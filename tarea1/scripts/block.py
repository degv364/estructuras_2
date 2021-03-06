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

#Regular Write-back block class
class Block_MVI():
    #Constructor of the class Block_MVI
    def __init__(self, n_state="i", n_tag=None, n_data=[]):
        self.state = n_state #Three possible values: m (modified), v (valid), i (invalid) 
        self.tag = n_tag
        self.data = n_data  #Data is a list of bytes
        
    #Function that invalidates block
    def invalidate(self):
        self.state="i"

#MESI protocol block class
class Block_MESI():
    #Constructor of the class Block_MESI
    def __init__(self, n_state="i", n_tag=None, n_data=[], n_setid=None):
        self.state = n_state
        self.tag = n_tag
        self.data = n_data  #Data is a list with every byte
        self.setid = n_setid

        
    #Function that reads a single byte from block as determined by offset
    def read(self, offset):
        return self.data[int(offset,2)]

    
    #Function that writes a single byte from block as determined by offset
    def write(self, offset, n_data):
        self.data[int(offset,2)] = n_data

        
    #Function in charge of handling FSM transition of block
    def fsm_transition(self, request, shared_flag = False): #Shared flag is used in miss cases
        flush = False #This flag indicates if a flush is required
        initial_state = self.state

        #Cases for block state
        if self.state == "m": flush = self._fsm_m(request, shared_flag)
        elif self.state == "e": self._fsm_e(request, shared_flag)
        elif self.state == "s": self._fsm_s(request, shared_flag)
        elif self.state == "i": self._fsm_i(request, shared_flag)
    
        return flush

    
    #Function that defines the FSM transition for 'm' case
    def _fsm_m(self, request, shared_flag):
        flush = False        
        if request == "Miss":
            if shared_flag:
                self.state = "s"
            else:
                self.state = "e"
            flush = True
        elif request == "PrRd":
            self.state = "m"
        elif request == "PrWr":
            self.state = "m"
        elif request == "BusRd":
            self.state = "s"
            flush = True
        elif request == "BusRdX":
            self.invalidate()
            
        return flush  #Asserts a flush if required

    #Function that defines the FSM transition for 'e' case
    def _fsm_e(self, request, shared_flag):
        if request == "Miss":
            if shared_flag:
                self.state = "s"
            else:
                self.state = "e"      
        elif request == "PrRd":
            self.state = "e"
        elif request == "PrWr":
            self.state = "m"
        elif request == "BusRd":
            self.state = "s"
        elif request == "BusRdX":
            self.invalidate()
            
    #Function that defines the FSM transition for 's' case
    def _fsm_s(self, request, shared_flag):
        if request == "Miss":
            if shared_flag:
                self.state = "s"
            else:
                self.state = "e"
        elif request == "PrRd":
            self.state = "s"
        elif request == "PrWr":
            self.state = "m"
        elif request == "BusRd":
            self.state = "s"
        elif request == "BusRdX":
            self.invalidate()
    
    #Function that defines the FSM transition for 'i' case
    def _fsm_i(self, request, shared_flag):
        if request == "Miss": 
            if shared_flag:
                self.state = "s"
            else:
                self.state = "e"

                
    #Function that invalidates block
    def invalidate(self):
        self.state = "i"

        
#Two way set (block pair) class. Applies LRU policy
class Block_pair():
    #Constructor of the class Block_pair
    def __init__(self, block1, block2):
        self.block1=block1
        self.block2=block2
        self.count1=0
        self.count2=0
        

    #Function that returns the LRU block (lowest score)
    def get_lru(self):
        #This will be used in case of miss. Block counter must return to 0
        if self.count1 <= self.count2:
            self.count1 = 0
            return self.block1
        else:
            self.count2 = 0
            return self.block2

        
    #Function that returns block with matching tag, or None in case of miss
    def get_by_tag(self, tag, update_count=True):
        #Every time the block is not used, the count is increased
        if self.block1.tag == tag and self.block1.state != "i":
            if update_count:
                self.count1 += 1
            return self.block1
        elif self.block2.tag == tag and self.block2.state != "i":
            if update_count:
                self.count2 += 1
            return self.block2
        else:
            #None has the tag or all are invalid, then it is a miss
            return None
