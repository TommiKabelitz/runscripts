from subprocess import run

from sources import *



def makeProp

run("mpirun","-np",numgpus,executable,"--solver='CGNE+S'","--itermax=1000000")
