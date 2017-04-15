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



class Block():

    def __init__(self, n_state, n_tag, n_data):
        self.state = n_state
        self.tag = n_tag
        self.data = n_data

    #Supposing tag is checked outside of the block
    def read(self):
        return self.data
            
    def write(self, n_data):
        self.data = n_data

    def fsm_transition(self, request, shared_flag = None): #Shared flag is used in miss cases
        flush = False
        if self.state == "m": flush = self._fsm_m(request, shared_flag)
        elif self.state == "e": self._fsm_e(request, shared_flag)
        elif self.state == "s": self._fsm_s(request, shared_flag)
        elif self.state == "i": self._fsm_i(request, shared_flag)
        return flush
            
            
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
            self.state = "i"
            flush = True
        return flush
            
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
            self.state = "i"
            
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
            self.state = "i"

    #FIXME: Check if other cases are necessary
    def _fsm_i(self, request, shared_flag):
        if request == "Miss": 
            if shared_flag:
                self.state = "s"
            else:
                self.state = "e"
                
            
    def invalidate(self):
        self.state = "i"
            
#this class will control the "recent of use"

class Block_pair():
    def __init__(self, block1, block2):
        self.block1=block1
        self.block2=block2
        self.count1=0
        self.count2=0
        #every time the block is not used, the count is increased
        #when asked for LRU, returns the block with highest score
        
    def get_lru(self):
        #this will be used in case of miss, then its counter must return to 0
        if self.count1>self.count2:
            self.count1=0
            return self.block1
        else:
            self.count2=0
            return self.block2

    def get_by_tag(self, tag):
        if self.block1.tag==tag and self.block1.state!="i":
            self.count2+=1
            return self.block1
        elif self.block2.tag==tag and self.block2.state!="i":
            self.count1+=1
            return self.block2
        else:
            #none has the tag or all are invalid, then is a miss
            return None

    def bus_need_tag(self, tag):
        #returns a block but needed by bus, then recent is not updated
        if self.block1.tag==tag and self.block1.state!="i":
            return self.block1
        elif self.block2.tag==tag and self.block2.state!="i":
            return self.block2
        else:
            return None


