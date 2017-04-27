#!/usr/bin/python
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


from utils import hex2bin

def get_addresses(filename):
    addresses=[]
    f=open(filename, 'r')
    content= f.read()
    content=content.split('\n')
    del content[-1]
    
    for line in content:
        if line[0]!='#': #to be able to add coments in instructions files
            [address, action]=line.split()
            address=hex2bin(address.split('x')[1])
            while len(address)<6:
                address="0"+address
            addresses.append([address, "{"+action+"}"])
    f.close()
    return addresses

'''
def get_addresses(filename):
    addresses=[]
    f=open(filename, 'r')
    content=f.read()
    content=content.split('\n')
    del content[-1]
    
    for line in content:
        [address, action]=line.split()
        hex_address = address[2:]
        bin_address = bin(int(hex_address, 16))[2:]
        #bin_address = bin(int(hex_address, 16))[2:].zfill(len(hex_address)*4)
        #print bin_address + " len: " + str(len(bin_address))
        addresses.append([bin_address, "{"+action+"}"])
        f.close()
    return addresses
'''

def test_parser():
    ins_list = get_addresses("test.txt")
    for ins in ins_list:
        print ins

if __name__=="__main__":
    test_parser()
