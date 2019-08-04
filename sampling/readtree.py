import treenode as tn
import plot as p
import random
import queue
import sys
from ssg import SSG, SSGElem
import logging
from operator import attrgetter

logger = logging.getLogger(__name__)

# set level to 'logging.DEBUG' to enable debug output for this module
logger.setLevel(logging.WARNING)

def computeSSG(nodes, upperbounds):
    """Compute SSG after entire tree has been read, and order of nodes is known

    Some nodes are never revisited, because they are not branched,
    and not removed either (probably cut off due to nonchronological backtracking).
    Therefore, we compute the ssg in an a-posteriori process
    """
    ssg = SSG()

    # we sort the nodes by the 'step' attribute
    nodes.sort(key = attrgetter("step"))

    ubidx = 0

    logger.debug("Upper Bounds at {}".format(upperbounds))

    for n in nodes:

        logger.debug("Node {}, Step {}".format(n.num, n.step))
        # update SSG whenever a new upper bound became available
        if ubidx < len(upperbounds):
            ubstep, ub = upperbounds[ubidx]
            update = False

            # loop through upper bounds as long as the node step count has not been reached.
            while ubstep < n.step:
                update = True
                ubidx += 1
                if ubidx < len(upperbounds):
                    ubstep, ub = upperbounds[ubidx]
                else:
                    break
            if update:
                ssg.updateUpperbound(upperbounds[ubidx - 1][1])


        # add the children of the node.
        for c in n.children:
            ssg.addNode(c)

        # delete the node. Note that node 0, the parent of the root, is not added.
        if n.num > 0:
            ssg.deleteNode(n)

        # the root is special. As in SCIP, we always make a split into left and right subtree. This also leads
        # to a proper update of the SSG value, which is otherwise inconsistent at the root node
        if n.num == 1:
            ssg.splitChildren()



        n.ssg = ssg.getValue()


    logger.debug("SSG at termination: {}".format(str(ssg)))
    return ssg.getValue()

def readTree(filename,zeroPhi):
    f = open(filename, 'r')
    nodes = [tn.TreeNode(0, None)] # root node: num=0 parent=None
    nodes[0].ready = True
    upperBound = 1e+20
    lowerBound = None
    nodesSeen = 0
    visited = set()
    upperbounds = [] # save steps at which new incumbent solutions have been found


    print(">Reading Tree...")
    for step, line in enumerate(f):
        logger.debug(line)
        buf = line.split()
        cmd = buf[0]
        if cmd == 'N':
            ### NEW NODE ###
            parent = nodes[int(buf[1])]
            num = int(buf[2])
            if num % 100000 == 0:
                print(">Adding node",num,"...")
            parent.addChild(tn.TreeNode(num,parent))
            nodes.append(parent.children[-1])
            parent.children[-1].addlpValue(parent.lpValue)
            nodesSeen += 1
            nodes[-1].nodesSeen = nodesSeen

            # increase step counter of parent
            # increase step counter of node only until it has children
            if len(parent.children) == 0:
                parent.step = step

            if parent.num > 0 and not parent.num in visited:
              visited.add(parent.num)
              parent.nodesVisited = len(visited)

        elif cmd == 'I':
            ### UPDATE NODE INFO ###
            num = int(buf[1])
            cnode = nodes[num]
            cnode.addDepth(int(buf[2]))
            oldlpValue = cnode.lpValue
            cnode.addlpValue(float(buf[3]))

            cnode.addGains()
            cnode.parent.addPhi(zeroPhi)
            cnode.parent.markReady(nodesSeen, upperBound, lowerBound)

            # increase step counter of node only until it has children
            if len(cnode.children) == 0:
                cnode.step = step

            if cnode.parent.num > 0 and not cnode.parent.num in visited:
              visited.add(cnode.parent.num)
              cnode.parent.nodesVisited = len(visited)

        elif cmd == 'U':
            ### NEW GLOBAL UPPER BOUND ###
            upperBound = float(buf[1])
            upperbounds.append((step, upperBound))


        elif cmd == 'L':
            ### NEW GLOBAL LOWER BOUND ###
            lowerBound = float(buf[1])

        elif cmd == 'X':
            ### NODE INFEASIBLE OR FATHOMED ###
            num = int(buf[1])
            cnode = nodes[num]
            cnode.leaf = True
            cnode.parent.markReady(nodesSeen)
            # increase step counter of node only until it has children
            if len(cnode.children) == 0:
                cnode.step = step

            if not num in visited:
              visited.add(num)
              cnode.nodesVisited = len(visited)


            if cnode.lpValue >= 1e+20:
                if cnode.children != []: # tricky bug where an inner node is pruned and upper bounds change
                    cnode.lpValue = cnode.children[0].lpValue
                else:
                    cnode.addlpValue(upperBound) # infeasible leaves get current upper bound as lp value
                cnode.addGains()
                cnode.parent.addPhi(zeroPhi)

    f.close()
    tree = tn.Tree(nodes[1])
    tree.root.calcSubTreeSize()
    ssgvalue = computeSSG(nodes, upperbounds)
    logger.debug("SSG Value is {}".format(ssgvalue))
    tree.numNodes = nodesSeen
    print('Total tree size (number of nodes) = {}'.format(nodesSeen))
    print('Total nodes visited = {}'.format(len(visited)))

    return tree

def readSVBTree(left,right,gap):
    def processSVBNode(node):
        if node.num == 1:
            node.lpValue = 0
        else:
            node.lpValue = node.parent.lpValue + [left,right][node.leftorright]
        if node.lpValue < gap:
            node.addChild(tn.TreeNode(2,node))
            node.children[0].depth = node.depth + 1
            processSVBNode(node.children[0])
            node.addChild(tn.TreeNode(2,node))
            node.children[1].depth = node.depth + 1
            processSVBNode(node.children[1])
            node.gains = [left,right]
            node.addPhi(0.9)
    print("Generating SVB tree...")
    dummyroot = tn.TreeNode(0,None)
    root = tn.TreeNode(1,dummyroot)
    root.depth = 0
    processSVBNode(root)
    tree = tn.Tree(root)
    tree.root.calcSubTreeSize()
    return tree

def readMVBTree(gap,variables):
    """
    Essentially runs SVB on the 'best' variable
    """
    def processMVBNode(node):
        if node.lpValue < gap:
            for i in range(2):
                node.addChild(tn.TreeNode(2,node))
                node.children[i].depth = node.depth + 1
                node.children[i].lpValue = node.lpValue + [left,right][i]
                processMVBNode(node.children[i])
            node.gains = [left,right]
            node.addPhi(0.9)
    variables.sort(key=(lambda v: v[0]*v[1]))
    left, right = variables[-1]
    print("Generating MVB tree...")
    dummyroot = tn.TreeNode(0,None)
    root = tn.TreeNode(1,dummyroot)
    root.depth = 0
    root.lpValue = 0
    processMVBNode(root)
    tree = tn.Tree(root)
    tree.root.calcSubTreeSize()
    return tree

def readGVBTree(gap,variables): # format for variables: [((l,r),n),((l,r),n),...]

    def processGVBNode(node,variables):
        if node.lpValue >= gap:
            return
        if len(variables) == 0:
            print("All variables exhausted, but gap not closed: Exiting...")
            sys.exit()
        if variables[-1][1] == 1:
            left, right = variables.pop()[0]
        else:
            left, right = variables[-1][0]
            variables[-1][1] -= 1
        for i in range(2):
            node.addChild(tn.TreeNode(2,node))
            node.children[i].depth = node.depth + 1
            node.children[i].lpValue = node.lpValue + [left,right][i]
            processGVBNode(node.children[i],variables[:]) # limits apply to branches, not the whole tree
        node.gains = [left,right]
        node.addPhi(0.9)

    print("Generating GVB tree...")
    variables.sort(key=(lambda v: v[0][0]*v[0][1])) # we use the best variables first; maybe change this
    dummyroot = tn.TreeNode(0,None)
    root = tn.TreeNode(1,dummyroot)
    root.depth = 0
    root.lpValue = 0
    processGVBNode(root,variables)
    tree = tn.Tree(root)
    tree.root.calcSubTreeSize()
    return tree
