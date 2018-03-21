import sys
import math

filename = sys.argv[1] # give it a .total file, remove path
name, pe, ou, _ = filename.rsplit('/',1)[1].split('.') # strip file path and get parts
try:
    shift = int(sys.argv[2]) # skip the first [shift] samples
    step = int(sys.argv[3]) # take only every [step]th sample
except IndexError: # set both or get default
    shift = 0
    step = 1
infile = open(filename)
outfile = open("auc.info",'a')
estimates = []
for line in infile:
    estimates.append(float(line))
if len(estimates) <= shift:
    print("{}\tSMALLTREE".format(name))
    sys.exit()
treesize = estimates[-1] # assumes complete sampling
area = 0
count = 0
ind = shift
while ind < len(estimates):
    area += abs(treesize - estimates[ind])
    #lgQ = math.log(estimates[ind]/treesize)
    #area += lgQ*lgQ
    ind += step
    count += 1
totalave = area / count
relerr = abs(round(100*(totalave)/(treesize),2))
#relerr = totalave
outfile.write("{} {} {} {}\n".format(pe,ou,name,relerr))
print("{}\t{}".format(name,relerr))
