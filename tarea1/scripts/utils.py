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

def gen_random_addresses(quantity=100., min_val=0, max_val=int("F"*6, 16)):
    #generate random adresses, but in clusters, to simulate how real progams work
    addresses=[]
    counter=0
    while counter<quantity:
        mega_cluster_range=randint(128, 1024)
        mega_origin=randint(min_val,max_val-mega_cluster_range)
        mega_cluster_size=randint(512, 8192)
        mega_min=mega_origin
        mega_max=mega_origin+mega_cluster_range
        m=0
        addresses.append("#Mega Cluster of size:"+str(mega_cluster_size)+" and range:"+str(mega_cluster_range)+" ")
        while m<mega_cluster_size and counter<quantity:
            cluster_range=randint(32, 128)
            origin=randint(mega_min,mega_max-cluster_range)
            cluster_size=randint(32, 1024)
            i=0
            addresses.append("#Cluster of size:"+str(cluster_size)+" and range:"+str(cluster_range)+" ")
            while i<cluster_size and m<mega_cluster_size and counter<quantity:
                i+=1
                m+=1
                counter+=1
                address=hex(origin+randint(0, cluster_range))
                addresses.append(address)

    return addresses
            
        
    


def random_generator(file_size=100, file_name="default.txt", second_size=100, second_file=None):
    content="#Random generated file"
    adresses=gen_random_addresses(file_size)
    for line in adresses:
        content+="\n"+line+" "
        if randint(0, 1)==1:
            content+="L"
        else:
            content+="S"

    file_1=open(file_name, "w")
    file_1.write(content)
    file_1.close()
    
    if second_file is not None:
        content="#Random generated file"
        adresses=gen_random_addresses(second_size)
        for line in adresses:
            content+="\n"+line+" "
            if randint(0, 1)==1:
                content+="L"
            else:
                content+="S"

        file_2=open(second_file, "w")
        file_2.write(content)
        file_2.close()

def partition_n(big_list=range(128), num_parts=8):
    #if num_parts does not divide big list, the last part will be lost
    avg_len=int(len(big_list)/int(num_parts))
    result=[]
    part_start=0
    while part_start<len(big_list):
        result.append(big_list[part_start:part_start+avg_len])
        part_start+=avg_len

    return result

def get_last_state_averages(last_state_list):
    averages={"Miss cache L1 (1) rate (found in other cache)":0,
              "Miss cache L1 (2) rate (found in other cache)":0,
              "Miss cache L1 (1&2) rate (found in other cache)":0,
              "Miss cache L1 (1) rate (Request to Cache L2)":0,
              "Miss cache L1 (2) rate (Request to Cache L2)":0,
              "Miss cache L1 (1&2) rate (Request to Cache L2)":0,
              "Miss cache L1 (1) rate": 0,
              "Miss cache L1 (2) rate":0,
              "Miss cache L1 (1&2) rate": 0,
              "Miss cache L2 rate": 0}
    total=len(last_state_list)

    for last_state in last_state_list:
        averages["Miss cache L1 (1) rate (found in other cache)"]+=last_state["L1(1)"]["Miss_rate_with_L1"]/total
        averages["Miss cache L1 (2) rate (found in other cache)"]+=last_state["L1(2)"]["Miss_rate_with_L1"]/total
        averages["Miss cache L1 (1&2) rate (found in other cache)"]=averages["Miss cache L1 (1) rate (found in other cache)"]*0.5+averages["Miss cache L1 (2) rate (found in other cache)"]*0.5
        
        averages["Miss cache L1 (1) rate (Request to Cache L2)"]+=last_state["L1(1)"]["Miss_rate_with_L2"]/total
        averages["Miss cache L1 (2) rate (Request to Cache L2)"]+=last_state["L1(2)"]["Miss_rate_with_L2"]/total
        averages["Miss cache L1 (1&2) rate (Request to Cache L2)"]=averages["Miss cache L1 (1) rate (Request to Cache L2)"]*0.5+averages["Miss cache L1 (2) rate (Request to Cache L2)"]*0.5
        
        averages["Miss cache L1 (1) rate"]=averages["Miss cache L1 (1) rate (found in other cache)"]+averages["Miss cache L1 (1) rate (Request to Cache L2)"]
        averages["Miss cache L1 (2) rate"]=averages["Miss cache L1 (2) rate (found in other cache)"]+averages["Miss cache L1 (2) rate (Request to Cache L2)"]
        averages["Miss cache L1 (1&2) rate"]=averages["Miss cache L1 (1) rate"]*0.5+averages["Miss cache L1 (2) rate"]*0.5
        
        averages["Miss cache L2 rate"]+=last_state["L2"]["Miss_rate"]/total

    print "\n ===Averages===\n"
    print "Average miss rate cache L1 = "+str(averages["Miss cache L1 (1&2) rate"])
    print "--found in the other cache L1 = "+str(averages["Miss cache L1 (1&2) rate (found in other cache)"])
    print "--Request to cache L2 = "+str(averages["Miss cache L1 (1&2) rate (Request to Cache L2)"])
    print "Average miss rate cache L2 = "+str(averages["Miss cache L2 rate"])

    return averages
