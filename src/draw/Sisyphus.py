from math import radians, sqrt
from sandable import Sandable
from Sand import THR_PATH
from dialog import DialogFile, DialogFloat, DialogList
from Chains import Chains
from thr import loadThr
import logging

class Sander(Sandable):
    """
### Draw Sisyphus tracks

#### Hints

Download tracks from [Dropbox](https://www.dropbox.com/sh/n2l29huvdrjalyx/AAA69jTy1aDobkR_wKog1Ewka?dl=0)

#### Parameters

* **File Name** - name of the file to be drawn.  Files use a rudimentary file browser that supports
  directories.  Search through the directories to find interesting things to draw.
"""

    def __init__(self, width, length, ballSize, units):
        self.ballSize = ballSize
        self.multiplier = min(width, length) / 2.
        self.xc, self.yc = width / 2, length / 2
        self.fullRadius = sqrt(max(width, length)**2)

        self.backgrounds = ['None', 'Spiral', "Full Spiral"]

        self.editor = [
            DialogFile("filename",            "File Name",                default=THR_PATH, filter='.thr'),
            DialogFloat("rotation",            "Rotation",                units='Degrees', default=0, min=-360., max=360.),
            DialogList("background",          "Background",               default='None', list=self.backgrounds),
        ]

    def generate(self, params):
        chain = []
        background = []
        filename = params.filename
        multiplier = self.multiplier
        xc, yc = self.xc, self.yc
        aplus = radians(params.rotation)
        logging.info("filename: %s xc:%d  yc:%d", filename,xc,yc)
        print(('filename: %s xc:%d  yc:%d' % (filename,xc,yc)))
        if filename.endswith('.thr'):
            chain = loadThr(filename, xc, yc, aplus, multiplier)
            if params.background == 'Spiral':
                turns = int(self.multiplier / self.ballSize)
                background = Chains.spiral(xc, yc, self.multiplier, 0, turns=turns, angleRate=7.)
            elif params.background == 'Full Spiral':
                turns = int(self.fullRadius / self.ballSize)
                background = Chains.spiral(xc, yc, self.fullRadius, 0, turns=turns, angleRate=7.)

        logging.info("Sisyphys chain size: %d", len(chain))
        return [background, chain]
