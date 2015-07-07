# -*- coding: utf-8 -*-
__author__ = 'Andres'

import argparse

parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true")
group.add_argument("-q", "--quiet", action="store_true")

parser.add_argument('directory', metavar='D', type=str, nargs='1',
                   help='output directory for the json files')

parser.add_argument('inputfile', metavar='I', type=str, nargs='2',
                   help='wikipedia dump file relative or full path')


args = parser.parse_args()
answer = args.x**args.y

if args.quiet:
    print(answer)
elif args.verbose:
    print("{} to the power {} equals {}".format(args.x, args.y, answer))
else:
    print("{}^{} == {}".format(args.x, args.y, answer))



#_------------------------
"""
parser = argparse.ArgumentParser(description='Parse Estonian Wikipedia dump file to Article Name.json files in a specified folder')


parser.add_argument('--sum', dest='accumulate', action='store_const',
                   const=sum, default=max,
                   help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))"""