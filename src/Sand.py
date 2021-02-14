# List of supported drawing classes
import platform
drawers = [
    "Spiral", "Rose", "Star",
    "Fermat", "Spirograph", "Sines",
    "Lissajous", "Harmonograph", "Nautilus",
    "GoldenDrop", "GoldenPop", "Shape",
    "Text", "Maze", "Sun",
    "Snowflake", "Dragon", "Hilbert",
    "Waves", "Grid", "Checkers",
    "Lorenz", "Shingles", "Lindenmayer",
    "Rocks", "Wood", "Grass",
    "WebPic", "Clipart", "Picture",
    "Sisyphus", "GCode", "Func3d", "SpiralArms",
    "Bulbs", "Engine", "ESpiral",
    "Man", "RandomDraw", "Move",
]

todo = ["Tree", "Celtic", "LOGO", "GreekKey", "CropCircle", "Propogation", ]

# List of LED patterns
# ledPatterns = [
#     "Off", "On", "Rainbow",
#     "Pastel", "Marquee", "Kaleidoscope",
#     "Orbit", "Distortion", "LightBall",
#     "OneColor", "LightHouse", "Dots",
#     "Holidays", "Fire", "Ocean",
#     "Clock", "Heartbeat", "RandomLights",
#     "Balloon", "Sky", "Emitter",
# ]

ledPatterns = [
    "Light-Params",
	"Static",
	"Blink",
	"Breath",
	"Color-Wipe",
	"Color-Wipe-Inverse",
	"Color-Wipe-Reverse",
	"Color-Wipe-Reverse-Inverse",
	"Color-Wipe-Random",
	"Random-Color",
	"Single-Dynamic",
	"Multi-Dynamic",
	"Rainbow",
	"Rainbow-Cycle",
	"Scan",
	"Dual-Scan",
	"Fade",
	"Theater-Chase",
	"Theater-Chase-Rainbow",
	"Running-Lights",
	"Twinkle",
	"Twinkle-Random",
	"Twinkle-Fade",
	"Twinkle-Fade-Random",
	"Sparkle",
	"Flash-Sparkle",
	"Hyper-Sparkle",
	"Strobe",
	"Strobe-Rainbow",
	"Multi-Strobe",
	"Blink-Rainbow",
	"Chase-White",
	"Chase-Color",
	"Chase-Random",
	"Chase-Rainbow",
	"Chase-Flash",
	"Chase-Flash-Random",
	"Chase-Rainbow-White",
	"Chase-Blackout",
	"Chase-Blackout-Rainbow",
	"Color-Sweep-Random",
	"Running-Color",
	"Running-Red-Blue",
	"Running-Random",
	"Larson-Scanner",
	"Comet",
	"Fireworks",
	"Fireworks-Random",
	"Merry-Christmas",
	"Fire-Flicker",
	"Fire-Flicker-(soft)",
	"Fire-Flicker-(intense)",
	"Circus-Combustus",
	"Halloween",
	"Bicolor-Chase",
	"Tricolor-Chase" ]

# Constants
SERVER_LOG = "/var/log/sandtable.log"

ROOT_DIRECTORY = "/var/www/sandtable"
DATA_PATH = "data/"
PICTURE_PATH = "pictures/"
CLIPART_PATH = "clipart/"
THR_PATH = "thr/"
GCODE_PATH = "gcode/"
MOVIE_SCRIPT_PATH = "scripts/"
MOVIE_OUTPUT_PATH = "movies/"
STORE_PATH = "store/"
SOURCE_PATH = "src/"
CONFIG_PATH = "config"
TMP_PATH = "/tmp/"

MACH_HOST = 'localhost'
MACH_PORT = 5007
MACH_LOG = "/var/log/machd.log"

VER_FILE = "%smachine.py" % DATA_PATH

IMAGE_FILE = "%spath.png" % DATA_PATH
IMAGE_WIDTH = 400

CACHE_FILE = "%ssandtable.pkl" % TMP_PATH

HISTORY_COUNT = 20

MOVIE_STATUS_LOG = "%smovie_progress" % TMP_PATH
MOVIE_STATUS_FILE = "%smovie_status.pkl" % TMP_PATH
MOVIE_WIDTH = 864
MOVIE_HEIGHT = 576

LED_HOST = 'localhost'
LED_PORT = 5008
LED_LOG = "/var/log/ledaemon.log"

SCHEDULER_HOST = 'localhost'
SCHEDULER_PORT = 5009
SCHEDULER_LOG = "/var/log/scheduler.log"

# Import machine specific configuration. This is done through a hostmap file
# located in the machines subdirectory.
HOST_NAME = platform.node()
print("Hostname lookup:", HOST_NAME)
exec("from %s.hostmap import hostmap" % CONFIG_PATH)
if HOST_NAME not in hostmap:
    print("hostname not found in map. Switching to 'default'")
    HOST_NAME = 'default'
exec("from %s.%s import *" % (CONFIG_PATH, hostmap[HOST_NAME]))

IMAGE_HEIGHT = int(IMAGE_WIDTH * (TABLE_LENGTH / TABLE_WIDTH))
MACH_FILE = '%smachines/%s.py' % (SOURCE_PATH, MACHINE)
