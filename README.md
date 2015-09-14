#badPixelMasker.py
Author: Jesse A. Rogerson, jesserogerson.com, email: rogerson@yorku.ca


-----
### Synopsis

This is an program designed to interpolate out bad pixels or cosmic rays of a spectrum. It uses a simple 1-dimensional interpolator to do this, and is fully interactive with the user.

###For Help:

$> ./badPixelMasker.py -h

usage: badPixelMasker.py [-h] [-zem ZEM] [-kind KIND] spec

positional arguments:
  spec        /path/to/normalized/ASCII/spectrum

optional arguments:
  -h, --help  show this help message and exit
  -zem ZEM    redshift of target (If provided, will assume you want to shift
              to rest-frame).
  -kind KIND  Type of interpolation. i.e., linear, nearest, zero, slinear,
              quadratic, cubic. See: scipy.interpolate.interp1d.html

###Outputs:
The program doesn't necessarily output anything. However, the user can opt to output an updated version of the input spectrum. It will be given the filename:

*filename.bpm.ascii*

wherein 'bpm' stands for Bad Pixel Masker. The output file will be exactly the same as the input file except the flux values in wavelength range(s) given during the masking process will have been changed.

###Notes:
a) BPM generates a plot for the user to interact with during the masking process. As a result, the user must be able to have figures pop-up. i.e., turn on x-11 forwarding.


### Installation

No Installation needed, just download and execute script.

### License

see LICENSE.txt
