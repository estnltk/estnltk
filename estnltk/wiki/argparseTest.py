# -*- coding: utf-8 -*-
__author__ = 'Andres'

import argparse

parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')


parser.add_argument('directory', metavar='D', type=str,
                   help='output directory for the json files')

parser.add_argument('inputfile', metavar='I', type=str,
                   help='wikipedia dump file relative or full path')

#group = parser.add_mutually_exclusive_group()
#group.add_argument("-v", "--verbose", action="store_true")
#group.add_argument("-q", "--quiet", action="store_true")

args = parser.parse_args()

if args.inputfile[-3:] == 'bz2':
    print('BZ2', args.inputfile)
elif  args.inputfile[-3:] == 'xml':
    print('XML', args.inputfile)
else:
    print("WRONG FILE FORMAT!")



#_------------------------
"""
parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')


parser.add_argument('--sum', dest='accumulate', action='store_const',
                   const=sum, default=max,
                   help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))"""