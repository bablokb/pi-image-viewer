#-----------------------------------------------------------------------------
# Simple image-viewer based on pygame and an APDS9960 for gesture control.
#
# This is really only a viewer without any additional features. Use case
# is an environment where you want to scroll around only with gestures, e.g.
# because your hands are dirty.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/pi-image-viewer
#-----------------------------------------------------------------------------

# system imports
import sys, locale, time, threading
from   argparse import ArgumentParser

# imports for APDS9960 gesture sensor
import board
import busio
from adafruit_apds9960.apds9960 import APDS9960

# imports for pygame
import pygame
from pygame.locals import *
from pygame.rect import *

DEFAULT_PAGING = 0.5
BG_COLOR       = (150, 150, 150)
FRAMERATE      = 30

# --- application class   ----------------------------------------------------

class Viewer(object):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    parser = self._get_parser()
    parser.parse_args(namespace=self)
    self.paging = self.paging[0]

    try:
      w,h = self.size[0].split(',')
    except:
      w,h = 0,0
    self.width  = int(w)
    self.height = int(h)

    if self.reverse:
      self._MAP = {
        K_LEFT:   self._right,
        K_RIGHT:  self._left,
        K_DOWN:   self._up,
        K_UP:     self._down,
        K_ESCAPE: self._close
      }
    else:
      self._MAP = {
        K_RIGHT:  self._right,
        K_LEFT:   self._left,
        K_UP:     self._up,
        K_DOWN:   self._down,
        K_ESCAPE: self._close
      }
    self._stop = None

    # initialize gesture-sensor
    try:
      i2c = board.I2C()
      self._apds = APDS9960(i2c)
      self._apds.proximity_gain = 3
      self._apds.enable_proximity = True
      self._apds.gesture_gain   = 3                       # 8x (i.e. max)
      self._apds.enable_gesture = True
      self._have_sensor = True
    except:
      self._have_sensor = False
      self._msg("Warning: could not detect APDS9960",force=True)

  # --- cmdline-parser   -----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Pi Image Viewer')

    parser.add_argument('-p', '--paging', nargs=1, type=float,
      metavar='paging', default=[DEFAULT_PAGING],
      dest='paging',
      help='relative amount for paging (e.g. 0.5: half of screen')
    parser.add_argument('-s', '--size', nargs=1,
      metavar='viewer-size',
      default=["0,0"],
      dest='size',
      help='size of the viewer x,y (default: maximize window)')

    parser.add_argument('-f', '--fullscreen', action='store_true',
      dest='fullscreen', default=False,
      help="use fullscreen-mode")
    parser.add_argument('-r', '--reverse', action='store_true',
      dest='reverse', default=False,
      help="swap behavior of up/down and left/right")

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('image', metavar='image',
      help='path to image')
    return parser

  # --- print message   ------------------------------------------------------

  def _msg(self,text,force=False):
    """ print debug-message """

    if force:
      sys.stderr.write("%s\n" % text)
    elif self.debug:
      sys.stderr.write("[DEBUG %s] %s\n" % (time.strftime("%H:%M:%S"),text))
    sys.stderr.flush()

  # --- print position of rectangle   ----------------------------------------

  def _dump_rect(self,label,r):
    self._msg(f"{label}: (x,y,w,h): ({r.x},{r.y},{r.w},{r.h})")

  # --- run gesture-detection   ----------------------------------------------

  def _process_gestures(self,init=False):
    """ process gestures """

    if not self._have_sensor:
      return

    if init:
      threading.Thread(target=self._process_gestures).start()
      return

    ev_dict = {}
    ev_dict['unicode'] = None

    # wait until system is up
    while self._stop is None:
      time.sleep(1)

    # simulate key-events
    self._msg(f"_process_gestures: running")
    while not self._stop.is_set():
      time.sleep(0.1)

      gesture = self._apds.gesture()
      if not gesture:
        continue

      self._msg(f"_process_gestures: gesture: {gesture}")
      if gesture == 0x01:
        ev_dict['key'] = pygame.K_UP
      elif gesture == 0x02:
        ev_dict['key'] = pygame.K_DOWN
      elif gesture == 0x03:
        ev_dict['key'] = pygame.K_LEFT
      elif gesture == 0x04:
        ev_dict['key'] = pygame.K_RIGHT

      event = pygame.event.Event(pygame.KEYDOWN,ev_dict)
      pygame.event.post(event)

  # --- run application   ----------------------------------------------------

  def run(self):
    """ run application """

    pygame.init()
    flags = pygame.FULLSCREEN if self.fullscreen else 0
    self.screen = pygame.display.set_mode((self.width,self.height),flags=flags)
    self.width,self.height = self.screen.get_size()
    self._msg(f"size: ({self.width},{self.height})")
    
    clock = pygame.time.Clock()
    moving = False 
    img = pygame.image.load(self.image)
    img.convert()
    self._img = img.get_rect()

    self._process_gestures(True)
    self._stop = threading.Event()
    while not self._stop.is_set():
      for event in pygame.event.get():
        if event.type == QUIT:
          self._close()
        elif event.type == KEYDOWN:
          if event.key in self._MAP:
            self._MAP[event.key]()
    
        elif event.type == MOUSEBUTTONDOWN:
          moving = True
        elif event.type == MOUSEBUTTONUP:
          moving = False
        elif event.type == MOUSEMOTION and moving:
          self._img.move_ip(event.rel)
    
      self.screen.fill(BG_COLOR)
      self.screen.blit(img,self._img)
      pygame.display.flip()
      clock.tick(FRAMERATE)

  # --- process key right   --------------------------------------------------

  def _right(self):
    """ scroll right by moving the image left """

    self._dump_rect("img",self._img)
    vx = self.paging*self.width
    if self._img.x - vx < -(self._img.w-self.width):
      vx = self._img.x + (self._img.w-self.width)
    self._img.move_ip((-vx,0))
    self._msg(f"vx: {-vx}")
    self._dump_rect("img",self._img)

  # --- process key left   ---------------------------------------------------

  def _left(self):
    """ scroll left by moving the image right """

    self._dump_rect("img",self._img)
    vx = self.paging*self.width
    if self._img.x + vx > 0:
      vx = -self._img.x             # vx is positive
    self._img.move_ip((vx,0))
    self._msg(f"vx: {vx}")
    self._dump_rect("img",self._img)

  # --- process key up   -----------------------------------------------------

  def _up(self):
    """ scroll up by moving the image down """

    self._dump_rect("img",self._img)
    vy = self.paging*self.height
    if self._img.y + vy > 0:
      vy = -self._img.y             #vy is positive
    self._img.move_ip((0,vy))
    self._msg(f"vy: {vy}")
    self._dump_rect("img",self._img)

  # --- process key down   ---------------------------------------------------

  def _down(self):
    """ scroll down by moving the image up """

    self._dump_rect("img",self._img)
    vy = self.paging*self.height
    if self._img.y - vy < -(self._img.h-self.height):
      vy = self._img.y + (self._img.h-self.height)
    self._img.move_ip((0,-vy))
    self._msg(f"vy: {-vy}")
    self._dump_rect("img",self._img)

  # --- close window and quit   ----------------------------------------------

  def _close(self):
    """ signal close to all threads """
    self._stop.set()

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = Viewer()
  app.run()
  pygame.quit()
