#!/usr/bin/python3 -u
import os
import sys
import traceback
import math

from optparse import OptionParser

from xml.sax.handler import ContentHandler
from xml.sax import parse

from Sand import MOVIE_WIDTH, MOVIE_HEIGHT, MOVIE_SCRIPT_PATH, MOVIE_OUTPUT_PATH,\
    TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS, TMP_PATH,\
    MACHINE_FEED, MACHINE_UNITS, drawers
from sandable import sandableFactory
from Chains import Chains
from dialog import Params
import mach
import camera
import MovieStatus

MOVIE_FORMAT = 'frame%04d.png'
MOVIE_SIZE = '%dx%d' % (MOVIE_WIDTH, MOVIE_HEIGHT)
MOVIE_BIT_RATE = 1800


class Movie:
    def __init__(self, Name='Unknown', FPS=5):
        self.Name = Name
        self.FPS = int(FPS)
        self.eraser = None
        self.frames = []

    def __repr__(self):
        return 'Movie(%s, %d, %s, %s)' % (self.Name, self.FPS, self.eraser, self.frames)

    def addEraser(self, eraser):
        self.eraser = eraser

    def addFrame(self, frame):
        self.frames.append(frame)

    def setData(self, data):
        self.data = data


class Eraser:
    def __init__(self):
        self.things = []
        self.lights = []

    def __repr__(self):
        return 'Eraser(%s, %s)' % (self.lights, self.things)

    def addThing(self, thing):
        self.things.append(thing)

    def addLight(self, light):
        self.lights.append(light)

    def setData(self, data):
        self.data = data


class Frame:
    def __init__(self, Steps=0, Repeat=1):
        self.Steps = int(Steps)
        self.Repeat = int(Repeat)
        self.things = []
        self.lights = []

    def __repr__(self):
        return 'Frame(%d, %d, %s, %s)' % (self.Steps, self.Repeat, self.lights, self.things)

    def addThing(self, thing):
        self.things.append(thing)

    def addLight(self, light):
        self.lights.append(light)

    def setData(self, data):
        self.data = data


class Thing:
    def __init__(self, Type, Name=None, Random=False):
        self.Type = Type
        self.Name = Name
        self.Random = Random
        self.params = {}

    def __repr__(self):
        return 'Thing(%s, %s, %s)' % (self.Type, self.Name, self.params)

    def addParam(self, param):
        self.params[param.Name] = param.Value

    def setData(self, data):
        self.data = data

    def has(self, name):
        return name in self.params

    def getvalue(self, name):
        return self.params[name]

    def interpolate(self, newThingy, steps):
        paramList = []
        for step in range(0, steps + 1):
            params = Params()
            for name, newValue in list(newThingy.params.__dict__.items()):
                oldValue = getattr(self.params, name)
                if isinstance(newValue, int):
                    setattr(params, name, int(round(oldValue + ((newValue - oldValue) * float(step) / steps))))
                elif isinstance(newValue, float):
                    setattr(params, name, oldValue + ((newValue - oldValue) * float(step) / steps))
                else:
                    setattr(params, name, newValue)

            paramList.append(params)
        return paramList


class Light(Thing):
    def __init__(self, Type):
        Thing.__init__(Type, Name="Light")

    def __repr__(self):
        return 'Light(%s, %s)' % (self.Type, self.params)


class Param:
    def __init__(self, Name=None, Value=None):
        # FIX: Fail if Name or Value is None
        self.Name = Name
        self.Value = Value

    def __repr__(self):
        return 'Param(%s,%s)' % (self.Name, self.Value)

    def setData(self, data):
        self.data = data


class ObjBuilder(ContentHandler):
    def __init__(self, class_names):
        ContentHandler.__init__(self)
        self.obj = []
        self._classes = class_names
        self.__buffer = []

    def startElement(self, name, attrs):
        self.__buffer = []
        if name not in self._classes:
            raise NameError(name)
        args = ['%s = "%s"' % (k, v) for k, v in list(attrs.items())]
        o = eval('%s(%s)' % (name, ','.join(args)))
        if self.obj:
            getattr(self.obj[-1], 'add' + name)(*(o,))
        else:
            self.rootobject = o
        self.obj.append(o)

    def endElement(self, name):
        if self.__buffer:
            self.obj[-1].setData(''.join(self.__buffer))
            self.__buffer = []
        del self.obj[-1]

    def characters(self, contents):
        self.__buffer.append(contents)


def build_class_hierarchy(classnames, file):
    handler = ObjBuilder(classnames)
    parse(file, handler)
    return handler.rootobject


class drawer:
    """Class used to draw individual frames either in preview mode or in sand
       If previewMode is True then images are drawn to PNG files
       If previewMode is False then drawing is done on the sand table and photos are taken
    """

    def __init__(self, previewMode, eraser, ms):
        self.previewMode = previewMode
        self.eraser = eraserToChains(eraser)
        self.ms = ms
        self.boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
        self.frameNumber = 0

    def draw(self, chain, repeat=1):
        self.ms.update(self.ms.ST_RUNNING, 'Drawing %04d' % self.frameNumber)
        if self.eraser and not self.previewMode:
            self.drawInSand(self.eraser)
        targetFrameNumber = self.frameNumber + repeat
        if self.previewMode:
            pic = Chains.makeRealisticImage(chain, self.boundingBox, MOVIE_WIDTH, MOVIE_HEIGHT)
            while self.frameNumber < targetFrameNumber:
                self.ms.update(self.ms.ST_RUNNING, 'Saving Frame %04d' % self.frameNumber)
                pic.save(TMP_PATH + (MOVIE_FORMAT % (self.frameNumber)), "PNG")
                self.frameNumber += 1
        else:
            self.drawInSand(chain)
            while self.frameNumber < targetFrameNumber:
                self.ms.update(self.ms.ST_RUNNING, 'Photographing Frame %04d' % self.frameNumber)
                camera.capture("%sIMG_%04d.jpg" % (TMP_PATH, self.frameNumber))
                self.frameNumber += 1

    def drawInSand(self, chains):
        with mach.mach() as e:
            e.run(chains, self.boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS, wait=True)


class Thingy:
    def __init__(self, type, name, params):
        self.Type = type
        self.Name = name
        self.params = params


def MakeMovie(script, previewMode, ms):
    ms.update(ms.ST_RUNNING, 'Processing "%s" %s' % (script, previewMode))

    # Parse the xml script file
    xmlFile = MOVIE_SCRIPT_PATH + script + '.xml'
    movie = build_class_hierarchy(["Movie", "Eraser", "Frame", "Thing", "Light", "Param"], xmlFile)
    print(movie)
    if not hasattr(movie, 'frames'):
        raise ValueError('First element of xml file must be <Movie>')

    # Draw the movie frames
    d = drawer(previewMode, movie.eraser, ms)
    oldThingies = []
    for frame in movie.frames:
        # Calculate an array of thingies (type, name, params) for later drawing
        thingies = []
        for thing in frame.things:
            # Import the sandable and invoke it
            if thing.Type not in drawers:
                raise ValueError('Unsupported Thing Type "%s"' % (thing.Type))
            print("Drawing thing:" + thing.Type)
            sand = sandableFactory(thing.Type, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)

            # Create the parameters
            # params = Params(sand.editor)
            params = Params()
            if thing.Random:
                params.randomize(sand.editor)
                print("Randomizing params")
            for field in sand.editor:
                if thing.has(field.name):
                    setattr(params, field.name, field.fromForm(thing.getvalue(field.name)))
                    print("Setting param:" + field.name + " to " + ('%s' % field.fromForm(thing.getvalue(field.name))) )

            thingies.append(Thingy(thing.Type, thing.Name, params))

        # No interpolation or morphing, just draw
        if frame.Steps <= 1:
            chains = []
            for thingy in thingies:
                sand = sandableFactory(thingy.Type, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
                chains += sand.generate(thingy.params)
            d.draw(chains, repeat=frame.Repeat)

        # Make intermediate chains
        else:
            stepChains = []
            for step in range(frame.Steps + 1):
                stepChains.append([])
            newMorphChains = []

            for thingy in thingies:
                oldThingy = findThingy(oldThingies, thingy.Name)
                sand = sandableFactory(thingy.Type, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)

                # If there was an old version, create chains by interpolating the parameters
                if oldThingy:
                    chains = interpolate(sand, oldThingy, thingy, frame.Steps)
                    for step in range(frame.Steps + 1):
                        stepChains[step] += chains[step]

                # Else, add to the morph chains
                else:
                    newMorphChains += sand.generate(thingy.params)

            if len(newMorphChains):
                if len(oldThingies):
                    oldMorphChains = []
                    for thingy in oldThingies:
                        sand = sandableFactory(thingy.Type, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
                        oldMorphChains += sand.generate(thingy.params)
                else:
                    oldMorphChains = newMorphChains

                chains = Chains.morph(oldMorphChains, newMorphChains, frame.Steps)
                for step in range(frame.Steps + 1):
                    stepChains[step] += chains[step]

            for step in range(frame.Steps + 1):
                d.draw(stepChains[step], repeat=frame.Repeat if step == frame.Steps else 1)

        oldThingies = thingies

    # Assemble all of the images into a movie
    if previewMode:
        outputFile = MOVIE_OUTPUT_PATH + script + '_preview.mp4'
        # ms.update(ms.ST_RUNNING, 'Using avconv to make the movie')
        ms.update(ms.ST_RUNNING, 'Using ffmpeg to make the movie')
        # os.system('avconv -r %d -i %s%s -b:%dk -y %s' % (movie.FPS, TMP_PATH, MOVIE_FORMAT, MOVIE_BIT_RATE, outputFile))

        os.system('ffmpeg -y -r %d -i %sframe%%04d.png -s %dx%d -crf 15 -vcodec libx264 -pix_fmt yuv420p %s' % (movie.FPS, TMP_PATH, MOVIE_WIDTH, MOVIE_HEIGHT, outputFile))
	# ffmpeg -r 60 -f image2 -s 500x500 -i /tmp/frame%04d.png -vcodec libx264 -crf 15 -pix_fmt yuv420p test.mp4

        ms.update(ms.ST_RUNNING, 'Cleaning up ".png" files')
        os.system('rm -v %s*.png' % TMP_PATH)
    else:
        outputFile = MOVIE_OUTPUT_PATH + script + '.mp4'
        # ms.update(ms.ST_RUNNING, 'Using avconv to make the movie')
        ms.update(ms.ST_RUNNING, 'Using ffmpeg to make the movie')
        # os.system('avconv -r %d -i %sIMG_%%04d.jpg -s:v %dx%d -y %s' % (movie.FPS, TMP_PATH, MOVIE_WIDTH, MOVIE_HEIGHT, outputFile))
        os.system('ffmpeg -y -r %d -i %sframe%%04d.png -s %dx%d -crf 15 -vcodec libx264 -pix_fmt yuv420p %s' % (movie.FPS, TMP_PATH, MOVIE_WIDTH, MOVIE_HEIGHT, outputFile))
	# ffmpeg -r 60 -f image2 -s 500x500 -i /tmp/frame%04d.png -vcodec libx264 -crf 15 -pix_fmt yuv420p test.mp4
        ms.update(ms.ST_RUNNING, 'Cleaning up the ".jpg" files')
        os.system('rm -v %s*.jpg' % TMP_PATH)

    return outputFile


def findThingy(thingies, name):
    if name:
        for i, thingy in enumerate(thingies):
            if thingy.Name == name:
                del thingies[i]
                return thingy
    return None


def interpolate(sand, oldThingy, newThingy, steps):
    chains = []
    for step in range(0, steps + 1):
        params = Params()
        for name, newValue in list(newThingy.params.__dict__.items()):
            oldValue = getattr(oldThingy.params, name)
            if isinstance(newValue, int):
                setattr(params, name, int(round(oldValue + ((newValue - oldValue) * float(step) / steps))))
            elif isinstance(newValue, float):
                setattr(params, name, oldValue + ((newValue - oldValue) * float(step) / steps))
            else:
                setattr(params, name, newValue)

        chains.append(sand.generate(params))
    return chains


def eraserToChains(eraser):
    if not eraser or not len(eraser.things):
        return None
    things = eraser.things
    chains = []
    for thing in things:
        # Import the sandable and invoke it
        if thing.Type not in drawers:
            raise ValueError('Unsupported Thing Type "%s"' % (thing.Type))
        sand = sandableFactory(thing.Type, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)

        # Create the parameters
        params = Params()
        for field in sand.editor:
            if thing.has(field.name):
                value = field.fromForm(thing.getvalue(field.name))
                setattr(params, field.name, value)
            else:
                setattr(params, field.name, field.default)

        chains += sand.generate(params)

    return chains


def intersects(circle, rect):
    xDistance = abs(circle.x - rect.x - rect.width / 2.0)
    yDistance = abs(circle.y - rect.y - rect.height / 2.0)
    if xDistance > (rect.width / 2.0 + circle.r) or yDistance > (rect.height / 2.0 + circle.r):
        return False
    if xDistance <= (rect.width / 2.0) or yDistance <= (rect.height / 2.0):
        return True
    cornerDistance = math.sqrt((xDistance - rect.width / 2.0) ^ 2 + (yDistance - rect.height / 2.0) ^ 2)
    return cornerDistance <= circle.r


def main():
    ms = MovieStatus.MovieStatus()
    try:
        ms.update(ms.ST_RUNNING, 'Starting Up')

        parser = OptionParser("usage: %prog [options]")
        parser.add_option("-p", "--sand",    dest="sand",    help="Draw in sand", default=False, action="store_true")

        (options, args) = parser.parse_args()

        if len(args) != 1:
            print('Expected script name as argument')
            raise ValueError("Script name wasn't passed as an argument")

        movieName = MakeMovie(args[0], not options.sand, ms)
        ms.update(ms.ST_DONE, 'Movie "%s" is finished' % movieName)

    except Exception:
        type, value, trace = sys.exc_info()
        ms.update(ms.ST_ERROR, 'Exited with\n' + ''.join(traceback.format_exception(type, value, trace)))


if __name__ == "__main__":
    main()
