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


from math import log, ceil
from random import randint
from time import sleep

def log2(num):
    return log(num, 2)

def log16(num):
    return log(num, 16)

def int2hex(integer, size):
    #returns a string that represents the integer, but with as many 0 to the left to fit size
    basic=hex(integer)[2:]
    if len(basic)>size:
        basic="x"*size
    else:
        while len(basic)<size:
            basic="0"+basic

    return basic

def int2bin(integer, size):
    #returns a string that represents the integer, but with as many 0 to the left to fit size
    basic=bin(integer)[2:]
    if len(basic)>size:
        basic="x"*size
    else:
        while len(basic)<size:
            basic="0"+basic

    return basic

def hex2bin(hex_value):
    return bin(int(hex_value, 16))[2:].zfill(len(hex_value)*4)

def bin2hex(bin_value):
    return hex(int(bin_value, 2))[2:].zfill(len(bin_value)/4).upper()


def debug_print(print_msg, print_queue, debug):
    if debug:
        print_queue.put(print_msg)


def random_generator(file_size=10, file_name="default.txt", second_size=10, second_file=None):
    content="#Random generated file"
    for line in xrange(file_size):
        content+="\n"+str(randint(0,int("F"*6,16)))+" "
        if randint(0, 1)==1:
            content+="L"
        else:
            content+="S"

    file_1=open(file_name, "w")
    file_1.write(content)
    file_1.close()
    
    if second_file is not None:
        content="#Random generated file"
        for line in xrange(second_size):
            content+="\n"+str(randint(0,int("F"*6,16)))+" "
            if randint(0, 1)==1:
                content+="L"
            else:
                content+="S"

        file_2=open(second_file, "w")
        file_2.write(content)
        file_2.close()
