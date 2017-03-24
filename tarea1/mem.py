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

def generate_block():
    block=[]
    for i in xrange(32):
        #generate 32 random bytes
        block.append(randint(0,255))

def mem(param_dicc):
    cmd_from_cache=param_dicc["cmd_from_cache"]
    data_from_cache=param_dicc["data_from_cache"]
    data_to_cache=param_dicc["data_to_cache"]

    #memory receives the same instructions as the caches, the address and if it is write/read
    while True:
        instruction=cmd_from_cache.recv()
        if instruction[1]=="{L}":
            #there was a miss and info from mem is required
            data_to_cache.send(generate_block())
        else:
            #there was a flush, and must receive data
            data=data_from_cache.recv()


    
