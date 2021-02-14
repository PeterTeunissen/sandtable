from math import sqrt, atan2, ceil, sin, cos
from Chains import Chains
import logging

"""
    GCode - 
    Load and save .gcode format files.
    Convert chains (polylines) into thr arrays.


G01 X193.819 Y142.497
G01 X193.729 Y142.522
G01 X193.557 Y142.554
G01 X193.301 Y142.570
G01 X192.966 Y142.543
"""


def loadGCode(filename, xc=0, yc=0, aplus=0, multiplier=1):
    """ Load GCode file """
    chain = []
    logging.info("start loading GCode file: %s", filename)
    print(('start loading GCode file: %s' % filename))
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith(';') or line.startswith('/') or not line:
                continue
            print("Gcode line:",line)
            if parts[0]=="G01":
                x=-1.0
                y=-1.0
                if parts[1].startswith('X'):
                    x=float(parts[1][1:])
                if parts[2].startswith('Y'):
                    y=float(parts[2][1:])
                if x!=-1.0 and y!=-1.0:
                    chain += [(x, y)]
                        
    logging.info("Done loading GCode file: %s", filename)
    return chain

