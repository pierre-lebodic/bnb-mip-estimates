import sys
import random as r

f = open("vars",'w')
n = int(sys.argv[1])
btype = sys.argv[2]
llower = 0
rupper = 1000
if btype == 'B':
    lupper = 1000
    rlower = 1
if btype == 'U':
    lupper = 500
    rlower = 501
if btype == 'V':
    lupper = 250
    rlower = 251
if btype == 'X':
    lupper = 100
    rlower = 101

for i in range(n):
    left = r.randint(llower,lupper)
    right = r.randint(rlower,rupper)
    if left > right:
        left, right = right, left
    f.write("{} {} {}\n".format(left,right,1))
