Pi-Image-Viewer
===============

This is a small image viewer with gesture-support. The viewer itself
has no extended features, more than viewing the image is not implemented.

Use case is a situation where you cannot use your hands to scroll, e.g.
you are viewing a recipe and have dirty hands but you want to page
forward or backward within the instruction.


Hardware
--------

For gesture-control, you need an APDS9960, a cheap gesture-sensor. The
sensor uses I2C, so you either need a SBC with I2C (like a Raspberry Pi),
or an USB-I2C bridge like the MCP2221.

A sufficiently large display is also needed, but since the viewer
implements scrolling, a small display would work, but would not be
very user-friendly.


Software
--------

The viewer is implemented in PyGame, sensor access uses Blinka. The installation
will install everything in a virtual environment. If your system is
not Debian-based, check the install-script in `tools/install` before
using it.


Installation
------------

To install, use the following commands:

    git clone https://github.com/bablokb/pi-image-viewer.git
    cd pi-image-viewer
    sudo tools/install

This installs a python virtual-environment in `/usr/local/lib/pi-image-viewer`
and a starter-script in `/usr/local/bin`.


Usage
-----

For a short help, run

    pi-image-viewer -h

Use `-f` to switch to fullscreen-mode or supply a window-size with
`-s width,height`. The default is to run in maximized mode.

The option `-p` controls the amount of paging. The default value of 0.5
will page by half of the screen-width, 1.0 would page a full-screen.

Navigation is either with the keyboard (arrow-keys) or using gestures.
"Right" will move the visible area of the image to the left, 
"up" will move it down. So the system behaves in the same as a 
smartphone or tablet. If this does not feel intuitive, use the `-r` 
switch to reverse this behavior.


Desktop Integration with pcmanfm
--------------------------------

For integration with the standard PiOS desktop file-manager, you need
a *.desktop-file to associate the pi-image-viewer with jpeg-images. To
automatically open these image-files with this application, you need
a file called `mimeapps.list`.

Ready to use examples are in the directory `pcmanfm`. Both files are
not automatically copied to your system, because you might need to
integrate the `mimeapps.list` into an existing file.

Standard locations of these files:

  - `$HOME/.config/mimeapps.list`
  - `$HOME/.local/share/applications/pi-image-viewer.deskop`
