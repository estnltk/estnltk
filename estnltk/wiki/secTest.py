__author__ = 'Andres'
# -*- coding: utf-8 -*-

from pprint import pprint

elems = [3,5,7]

#elems = [1,2,3,4,5,6,7,8,9]

n = len(elems)
pos = 0
stack = [[]]
levels = [elems[0]]

while pos < n:
    elem = elems[pos]
    level = levels[-1]
    if elem == level:
        stack[-1].append(elem)
    elif elem >= level:
        stack.append([elem])
        levels.append(elem)
    else:
        group = stack.pop()
        stack[-1].append(group)
        levels.pop()
        continue
    pos += 1

while len(stack) > 1:
    group = stack.pop()
    stack[-1].append(group)

print (elems)
pprint(stack[0])
