import sys

info = sys.argv[1]
f = open(info)
filenames = []
p = []
e = []
for line in f:
    pe, ou, filename, auc, *_ = line.split()
    if filename not in filenames:
        filenames.append(filename)
    if pe == "phi":
        p.append(float(auc))
    elif pe == "even":
        e.append(float(auc))
rel = [1 if e[i] == 0 else p[i]/e[i] for i in range(len(p))]
pwins = sum(1 if rel[i] < 1 else 0 for i in range(len(rel)))
ewins = sum(1 if rel[i] > 1 else 0 for i in range(len(rel)))
acc = 1
acc2 = 1
acc3 = 1
for val in rel:
    acc *= val
geoave = acc**(1/len(rel))
for val2 in p:
    if val2 != 0: acc2 *= val2
geoave2 = acc2**(1/len(p))
for val3 in e:
    if val3 != 0: acc3 *= val3
geoave3 = acc3**(1/len(e))
print("Num wins for phi: {}".format(pwins))
print("Num wins for even: {}".format(ewins))
print("Draws: {}".format(len(rel)-pwins-ewins))
print("Geometric average of phi: {}".format(geoave2))
print("Geometric average of even: {}".format(geoave3))
print("Geometric average of phi/even: {}".format(geoave))
