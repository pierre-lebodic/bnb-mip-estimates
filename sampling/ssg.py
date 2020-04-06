import logging

logger = logging.getLogger(__name__)

# set level to 'logging.DEBUG' to enable debug output for this module
logger.setLevel(logging.WARNING)

class SSGElem:
    def __init__(self, node):
        self.node = node
        self.lpValue = node.firstlpValue
        self.pqidx = -1

    def __cmp__(self, other):
        return self.lpValue - other.lpValue

    def __str__(self):
        return "SSGELEM({}, {})".format(self.node.num, self.lpValue)

class SSGPQueue:
    def __init__(self):
        self.elems = []

    def parent(self, i):
        return (i + 1) // 2 - 1

    def leftchild(self, i):
        return 2 * i + 1

    def rightchild(self, i):
        return 2 * i + 2

    def put(self, elem : SSGElem):
        # put the element at the end of the elems

        pos = len(self.elems)
        self.elems.append(elem)
        parent = self.parent(pos)

        # compare with parent and swap as long as this element is smaller
        while self.parent(pos) >= 0 and elem.__cmp__(self.elems[self.parent(pos)]) < 0:
            self.elems[pos] = self.elems[self.parent(pos)]
            self.elems[pos].pqidx = pos
            pos = self.parent(pos)

        # store the index
        self.elems[pos] = elem
        elem.pqidx = pos

    def deleteElem(self, elem):
        # swap this element with the last element
        pos = elem.pqidx

        logger.debug(elem)
        lastelem = self.elems[len(self.elems) - 1]
        self.elems.remove(lastelem)

        if lastelem == elem:
            return

        while self.parent(pos) >= 0 and lastelem.__cmp__(self.elems[self.parent(pos)]) < 0:
            self.elems[pos] = self.elems[self.parent(pos)]
            self.elems[pos].pqidx = pos
            logger.debug("Moved {} to position {}".format(str(self.elems[pos]), pos))
            pos = self.parent(pos)


        childpos = self.leftchild(pos)
        while childpos < len(self.elems):
            rightchildpos = self.rightchild(pos)

            if rightchildpos < len(self.elems) and self.elems[rightchildpos].__cmp__(self.elems[childpos]) < 0:
                childpos = rightchildpos

            logger.debug("Comparing {} to {}".format(lastelem, self.elems[childpos]))
            if lastelem.__cmp__(self.elems[childpos]) <= 0:
                break

            self.elems[pos] = self.elems[childpos]
            self.elems[pos].pqidx = pos
            logger.debug("Moved {} to position {}".format(str(self.elems[pos]), pos))
            pos = childpos
            childpos = self.leftchild(pos)


        # shuffle the element up or down to reinstall queue invariant
        self.elems[pos] = lastelem
        lastelem.pqidx = pos

    def min(self):
        if len(self.elems) > 0:
            return self.elems[0]
        else:
            return None

    def __str__(self):
        return "[{}]".format(", ".join(list(map(str, self.elems))))


class SSG:

    def __init__(self):
        self.value = 1.0
        self.scalingfactor = 1.0
        self.ub = 1e+20
        self.subtrees = [SSGPQueue()]
        self.subtreelabel = {}
        self.node2ssgelem = {}
        pass

    def splitChildren(self):
        if len(self.subtrees) == 1 and len(self.subtrees[0].elems) == 0:
            return
        logger.debug("Splitting")
        # loop over all elements of all priority queues, and label them individually
        nsubtrees = 0
        subtrees = []
        subtreelabel = {}
        node2ssgelem = {}
        gapsum = 0.0
        for pqueue in self.subtrees:
            for elem in pqueue.elems:
                newpq = SSGPQueue()
                subtrees.append(newpq)
                newpq.put(elem)
                gapsum += self.getGap(self.ub, elem.lpValue)
                subtreelabel[elem.node] = nsubtrees
                nsubtrees += 1

        self.scalingfactor = self.value / max(gapsum,1e-6)

        self.value = self.scalingfactor * gapsum;

        self.subtrees = subtrees
        self.subtreelabel = subtreelabel

        logger.debug("After Split: {} subtrees, {} value, {} scaling factor, {} gapsum".format(len(self.subtrees), self.getValue(), self.scalingfactor, gapsum))
        logger.debug("\n".join(map(str, self.subtrees)))

    def addNode(self, node):

        if node in self.subtreelabel:
            return
        ssgelem = SSGElem(node)
        self.node2ssgelem[node] = ssgelem
        label = self.subtreelabel.get(node.parent, 0)
        self.subtreelabel[node] = label
        self.subtrees[label].put(ssgelem)
        logger.debug("Added {} to subtree {}".format(ssgelem, label))
        logger.debug("Elements in Subtree {}:{}".format(label, self.subtrees[label]))

    def getValue(self):
        return self.value

    def getGap(self, ub, lb):
        if abs(ub) >= 1e+20 or abs(lb) >= 1e+20:
            return 1.0
        elif abs(ub - lb) < 1e-6:
            return 0.0
        else:
            return abs(ub - lb)/max(abs(ub), abs(lb))

    def deleteNode(self, node):
        if not node in self.node2ssgelem:
            return

        ssgelem = self.node2ssgelem[node]
        label = self.subtreelabel[node]
        logger.debug("Deleting {} from subtree {} (index {})".format(ssgelem, label, ssgelem.pqidx))
        self.subtrees[label].deleteElem(ssgelem)

        logger.debug("Min Elem {}, label {}".format(self.subtrees[label].min(), label))
        if ssgelem.pqidx == 0:
            logger.debug("Update, upper bound is {}".format(self.ub))
            oldgap = self.getGap(self.ub, ssgelem.lpValue)

            if not self.subtrees[label].min():
                newgap = 0.0
            else:
                newgap = self.getGap(self.ub, self.subtrees[label].min().lpValue)

            self.value += self.scalingfactor * (newgap - oldgap)
            logger.debug("New Gap {}, Old Gap {}".format(newgap, oldgap))
            assert (newgap - oldgap) <= 0

        del self.subtreelabel[node]
        del self.node2ssgelem[node]



    def updateUpperbound(self, newupperbound):
        logger.debug("New Upper Bound {}, was {}".format(newupperbound, self.ub))
        self.ub = newupperbound
        self.splitChildren()

    def __str__(self):
        nonemptysubtrees = [s for s in self.subtrees if len(s.elems) > 0]
        return "SSG, value {}, {} subtrees ({} nonempty). {}".format(self.getValue(), len(self.subtrees), len(nonemptysubtrees), str(nonemptysubtrees[0]) if len(nonemptysubtrees) > 0 else "")


if __name__ == "__main__":
    logger.debug("Hello")
    ssgpqueue = SSGPQueue()
    for i in [0,1,2,3,4,5,6]:
        logger.debug ("index %d, parent %d, left/right children %d/%d" % (i, ssgpqueue.parent(i), ssgpqueue.leftchild(i), ssgpqueue.rightchild(i)))

    mylist = [1,4,7]
    mylist[3] = 2
