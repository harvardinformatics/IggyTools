import os.path as path
from iggytools.utils.util import intersect, unique

class Vertex(object):
    def __init__(self, filename):
        self.name = filename
        self.parents = list()
        self.children = list()
        self.isExpired = False

    def addParents(self, Files):
        if type(Files) != list: Files = [Files]
        self.parents += [x.name for x in Files]

    def addChildren(self, Files):
        if type(Files) != list: Files = [Files]
        self.children += [x.name for x in Files]
    
class depGraph(object):
    def __init__(self):
        self.v = dict()  #vertices of the graph
        self.numExpired = 0  #number of expired vertices
        self.Tasks = list()
        self.altered = list()

    def isVertex(self, filename):
        if filename in self.v.keys():
            return True
        return False

    def addVertex(self, filename):
        if self.isVertex(filename): raise Exception('Vertex %s already added' % filename)
        self.v[filename] = Vertex(filename)

    def addTask(self, aTask):
        if len(intersect([x.name for x in aTask.inFiles], [x.name for x in aTask.outFiles])) != 0:
            raise Exception('Cannot have same filename in Task inFiles and outFiles. Task: %s' % aTask)

        for File in aTask.inFiles:
            if not self.isVertex(File.name): 
                self.addVertex(File.name)
            self.v[File.name].addChildren(aTask.outFiles)

        for File in aTask.outFiles:
            if not self.isVertex(File.name): 
                self.addVertex(File.name)
            self.v[File.name].addParents(aTask.inFiles)
            
        self.Tasks.append(aTask)

    def orderedTasks(self): #return tasks that must be preformed due to expired files, ordered by dependency
        orderedTasks = []

        # First, append tasks in an order so that all expired files are updated
        while self.numExpired > 0:
            for aTask in self.Tasks:
                allAncestors = list()
                for inFilename in [x.name for x in aTask.inFiles]:
                    allAncestors += self.getAncestors(inFilename)
                allAncestors = unique(allAncestors)
                if any([self.v[x.name].isExpired == True for x in aTask.outFiles])  \
                        and ( len(allAncestors) == 0 or all([self.v[x].isExpired == False for x in allAncestors]) ):
                    orderedTasks.append(aTask)

                    #mark task's expired output files as unexpired
                    for outFile in aTask.outFiles:
                        if self.v[outFile.name].isExpired:
                            self.v[outFile.name].isExpired = False
                            self.numExpired -= 1

        # Second, append tasks with untracked output files (but only those tasks whose input files have been altered)
        for aTask in self.Tasks:
            if not aTask.outFiles and len(intersect([x.name for x in aTask.inFiles], self.altered)):
                orderedTasks.append(aTask)

        return orderedTasks
                        
    def setExpired(self, modifiedFiles):  #mark descendants of modified files as expired
        if type(modifiedFiles) != list: modifiedFiles = [modifiedFiles]
        toExpire = []
        for File in modifiedFiles:
            if File.name in self.v.keys():
                toExpire += self.getDescendants(File.name)
        for filename in unique(toExpire):
            aVertex = self.v[filename]
            if aVertex.isExpired == False:
                aVertex.isExpired = True
                self.numExpired += 1
        self.altered += unique([x.name for x in modifiedFiles] + toExpire)

    def getAncestors(self, filename): #get all upstream vertices
        aVertex = self.v[filename]
        ancestors = aVertex.parents 
        for parent in aVertex.parents:
            temp = self.getAncestors(parent)
            ancestors += temp
        return unique(ancestors)


    def getDescendants(self, filename): #get all downtream vertices
        aVertex = self.v[filename]
        descendants = aVertex.children 
        for child in aVertex.children:
            descendants += self.getDescendants(child)
        return unique(descendants)
