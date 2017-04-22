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

import hex2bin

def get_addresses(filename):
    addresses=[]
    f=open(filename, 'r')
    content= f.read()
    content=content.split('\n')

    for line in content:
        [address, action]=line.split()
        address=hex2bin(address.split('x')[1])
        while len(address)<6:
            address="0"+address
        addresses.append([address, "{"+action+"}"])
    f.close()
    return addresses
