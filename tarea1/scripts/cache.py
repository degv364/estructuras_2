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


from math import log
from random import randint

def log2(num):
    return log(num, 2)

def log16(num):
    return log(num, 16)

def int2hex(integer, size):
    #returns a string that represents the integer, but with as meny 0 to the left to fit size
    basic=hex(integer)
    basic=basic.split('x')[1]
    if len(basic)>size:
        basic="x"*size
    else:
        while len(basic)<size:
            basic="0"+basic

    return basic

def int2bin(integer, size):
    #returns a string that represents the integer, but with as meny 0 to the left to fit size
    basic=hex(integer)
    basic=basic.split('b')[1]
    if len(basic)>size:
        basic="x"*size
    else:
        while len(basic)<size:
            basic="0"+basic

    return basic

def hex2bin(integer):
    length=len(integer) #how many chars in the number
    return int2bin(int(integer), 4*length) #evety hex symbols needs 4 bits

def bin2hex(integer):
    length=len(integer)
    return int2hex(int(integer), length/4)


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




def cacheL2(param_dicc):
    cache=Cache1w(128000, 32,param_dicc)
    cache.execution_loop() #FIXME: missing implementation

    


def cacheL1(param_dicc):
    #FIXME: missing implementation
    pass
    

