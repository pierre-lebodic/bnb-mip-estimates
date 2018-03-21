import sys

def compress(filename):
    prev = ""
    f = open(filename, 'r')
    g = open(filename.rsplit('.',1)[0]+".abc",'w')
    for line in f:
        buf = line.split()
        if buf[0] == '#':
            continue
        cmd = buf[1]
        if cmd == 'N':
            ### NEW NODE ###
            parent = int(buf[2])
            num = int(buf[3])
            g.write("N {} {}\n".format(parent,num))

        elif cmd == 'I':
            ### UPDATE NODE INFO ###
            num = int(buf[2])
            buf2 = buf[4].split("\\t")
            depth = int(buf2[1].split('\\')[0])
            if len(buf) == 5:
                lp = float(buf2[3].strip('\\nnr:'))
            if len(buf) == 8:
                lp = float(buf[7].split('\\')[2].strip('t'))
            out = "I {} {} {}\n".format(num,depth,lp)
            if out != prev:
                g.write(out)
            prev = out

        elif cmd == 'U':
            ### NEW GLOBAL UPPER BOUND ###
            upperBound = float(buf[2])
            g.write("U {}\n".format(upperBound))

        elif cmd == 'L':
            ### NEW GLOBAL LOWER BOUND ###
            lowerBound = float(buf[2])
            g.write("L {}\n".format(lowerBound))

        elif cmd == 'P' and buf[3] == '4':
            ### NODE INFEASIBLE OR FATHOMED ###
            num = int(buf[2])
            g.write("X {}\n".format(num))

    f.close()

compress(sys.argv[1])
