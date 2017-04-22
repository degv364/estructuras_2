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

def core(param_dicc):
    ins_list=param_dicc["instructions"]
    cmd_to_cache=param_dicc["cmd_to_cache"]
    data_from_cache=param_dicc["data_from_cache"]
    data_to_cache=param_dicc["data_to_cache"]

    sleep(0.5) #wait for the rest to initialize
    
    for instruction in ins_list:
        if instruction[1]="{L}":
            cmd_to_cache.send(instruction)
            #si la instruccion es de lectura
            data=data_from_cache.recv()
        else:
            #es de escritura, send info then command
            data_to_cache.send(randint(0,255))
            cmd_to_cache.send(instruction)
        sleep(1/100)

    print "finished execution..."
