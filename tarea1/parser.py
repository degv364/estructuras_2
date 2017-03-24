#!/usr/bin/python

def get_addresses(filename):
    addresses=[]
    f=open(filename, 'r')
    content= f.read()
    content=content.split('\n')

    for line in content:
        addresses.append(line.split())
    f.close()
    return addresses
