#!/usr/bin/env python
'''
--------------------------------------------------------------------------------
Author: Jesse A. Rogerson, jesserogerson.com, rogerson@yorku.ca

This is an program designed to interpolate out bad pixels or cosmic rays of a
spectrum. It uses a simple 1-dimensional interpolator to do this, and is fully
interactive with the user.

FOR HELP:
----------

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

OUTPUTS:
----------
The program doesn't necessarily output anything. However, the user can opt to
output an updated version of the input spectrum. It will be given the filename:

$> filename.bpm.ascii

wherein 'bpm' stands for Bad Pixel Masker. The output file will be exactly the
same as the input file exce:pt the flux values in wavelength range(s) given
during the masking process will have been changed.

NOTES:
----------
a) BPM generates a plot for the user to interact with during the masking
process. As a result, the user must be able to have figures pop-up. i.e., turn
on x-11 forwarding.

HISTORY
--------------------------------------------------------------------------------
2014-10-09 - JAR - created
2015-09-03 - JAR - converted to run off the commandline
2015-09-05 - JAR - Massive edits:
				 - now this program runs in a looping interactive mode
				 - the user has the ability to add/remove masked regions on the
				   fly, as well as write the new spectrum to file at anytime.
2015-09-05 - JAR - original commit to github.com/jesserogerson
2015-09-10 - JAR - added while loop to masking routine. asks users to confirm
				   the mask they just applied. Makes it easy to try different
				   masks quickly.
2015-09-14 - JAR - Will de-redshift the given spectrum if a zem is provided
--------------------------------------------------------------------------------
'''
import numpy as np
from sys import argv
import sys
from scipy.interpolate import interp1d
import argparse
import copy as cp
import matplotlib.pyplot as plt

#some global variables
yes=set(['yes','y','YES','Y',True,1])
no=set(['no','n','NO','N',False,0])
interpList=['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic']

def masking(**kwargs):
	'''
	An interactive, constantly looping program that masks out bad pixels
	as per the user's instructions
	'''
	filename=kwargs['spec']
	#zem=kwargs['zem']
	#smoothVal=kwargs['kind']
	interpFunction=kwargs['kind']

	#for writing to file later
	rootname=filename[0:filename.index('.')]
	suffix=filename[filename.index('.')+1:-1]+filename[-1]
	print '--------------------------------------------------------------------------------'
	print '--------------------------BAD PIXEL MASKER--------------------------'
	print '--------------------------------------------------------------------'
	print ''
	print 'Lets starting masking pixels... shall we?'
	print ''
	print 'Detected filename:',filename
	print 'Reading in ASCII table.'

	#Read in file first
	spectrum=np.genfromtxt(filename,usecols=(0,1,2))
	print 'Table shape:'+str(np.shape(spectrum))
	#validate table shape, yell if it didn't match lam,flux,fluxerr
	if np.shape(spectrum)[1]!=3:
		print '-----ERROR:'
		print '-----Data Array associated with this spectrum is INCORRECT shape.'
		print '-----Requires 3 columns: lambda,flux,flux_err.'
		print '-----...Exiting entire program'
		sys.exit()

	#Will shift into rest-frame if a zem is provided
	spectrum[:,0]=spectrum[:,0]/(1.+zem)

	#make a deep copy of the spectrum before going into loop
	#NEVER change 'spectrum', ... only change the copies
	lam=cp.deepcopy(spectrum[:,0])
	flux=cp.deepcopy(spectrum[:,1])
	flux_err=cp.deepcopy(spectrum[:,2])

	#Make a plot of the spctrum to interact with
	plt.rc('text',usetex=True)
	plt.rc('font',family='sans-serif')
	plt.ion()
	graph=plt.plot(lam,flux,'k')[0]
	scat=plt.scatter(lam,flux,s=10)
	plt.plot(lam,flux_err,'k')
	plt.xlabel('wavelength (\AA)')
	plt.ylabel('flux')
	plt.draw()

	#prepping the while loop
	escape=False 	#used to escape the while loop when the user is done
	first=False  	#I want to print out the 'commands' first, see below
	regionDict={} 	#a master dictionary of all the regions masked so far
	count=0			#needed to keep the master dictionary
	user_input='commands'	#initial command sent to loop
	while escape==False:
		#skips this the first time, ... want to first plot the commands
		if first==True:
			user_input=raw_input('Enter a command:')
		first=True

		#NOW... what did the user enter?
		if user_input=='q' or user_input=='Q':
			print '--------------------------------------------------------------------'
			print 'The regions you masked out were:'
			print regionDict
			print 'I hope you wrote that to file!!!'
			print 'EXITING....'
			print '--------------------------------------------------------------------'
			escape=True
		elif user_input=='commands':
			print '--------------------------------------------------------------------'
			print 'You can mask out various regions of the spectra you input'
			print 'by using the commands below.'
			print ''
			print 'q,Q          : to quit the Bad Pixel Masker'
			print 'mask         : mask a region'
			#print 'smooth		 : smooth the continuum [y,n]'
			print 'funcType     : change the interpolating function'
			print 'write        : write updated spectrum to file.'
			print 'regions		: display the regions you have masked already.'
			print 'commands     : display these commands again.'
			print '--------------------------------------------------------------------'
		elif user_input=='mask':
			ans=False
			while ans==False:
				print '--------------------------------------------------------------------'
				#Step1: ask user to locate the bad pixel
				print 'INSTRUCT: Use the figure to determine the location of the bad pixels.'
				user_input=raw_input('Enter wavelength range of bad pixel(s) (comma separated): ')
				region=map(float,user_input.split(','))
				print 'Region of bad pixels:'+str(region)
				#find the indexes that correspond to the wavelength limits
				bad_indexes=[index for index,value in enumerate(lam) if value >= region[0] and value <= region[1]]
				xlow=bad_indexes[0]
				xhigh=bad_indexes[-1]
				user_input=raw_input('Enter size of window to use either side of bad region: ')
				rad=int(user_input)+1
				print '------------------------------------------------------------'
				print 'Wavelength region of bad pixels selected:'+str(region)
				print 'This corresponds to indexes: '+str(xlow)+' to '+str(xhigh)
				print 'Chose to interpolate using',(rad-1),'pixels on either side of the bad region.'
				print 'Interpolating using indexes:  '+str(xlow-rad)+' to '+str(xlow-1)
				print '                              '+str(xhigh+1)+' to '+str(xhigh+rad)
				print 'Corresponding wavelength region: '+str(lam[xlow-rad])+' to '+str(lam[xlow-1])
				print '                                 '+str(lam[xhigh+1])+' to '+str(lam[xhigh+rad])
				print '...........................masking..........................'
				print '------------------------------------------------------------'
				#pull out the 'bad pixels'
				lam_bad=lam[xlow:xhigh+1]
				flux_bad=flux[xlow:xhigh+1]
				flux_err_bad=flux_err[xlow:xhigh+1]
				#Step2: calculate the interpolation function
				xnew=np.concatenate((lam[(xlow-rad):(xlow-1)],lam[(xhigh+1):(xhigh+rad)]))
				ynew=np.concatenate((flux[(xlow-rad):(xlow-1)],flux[(xhigh+1):(xhigh+rad)]))
				ynewerr=np.concatenate((flux_err[(xlow-rad):(xlow-1)],flux_err[(xhigh+1):(xhigh+rad)]))
				#fit a linear function, interpolate (1 dimensionally)
				f=interp1d(xnew,ynew, kind=interpFunction)
				#replace the values of flux with the new ones.
				for i in range(len(lam)):
					if i>=xlow and i<=xhigh:
						print lam_bad[i-xlow],flux_bad[i-xlow],'-->',f(lam_bad[i-xlow])
						flux[i]=f(lam_bad[i-xlow])
				#reset the graph, so the user can look
				graph.set_ydata(flux)
				scat.remove()
				scat=plt.scatter(lam,flux,s=10)
				plt.pause(0.01)
				user_input=raw_input('Do you want to keep these changes? [y/n]:')
				if user_input in yes:
					print 'Keeping mask, back to command page.'
					ans=True
					regionDict[count]=[region[0],region[1]]
					count+=1
				else:
					if user_input not in no:
						print 'Thats not an answer, removing the mask anyway.'
					for i in range(len(lam)):
						if i>=xlow and i<=xhigh:
							print lam[i],flux[i],'-->',spectrum[i,1]
							flux[i]=cp.deepcopy(spectrum[i,1])
					graph.set_ydata(flux)
					scat.remove()
					scat=plt.scatter(lam,flux,s=10)
					plt.pause(0.01)
			print '--------------------------------------------------------------------'
		elif user_input=='smooth':
			print '--------------------------------------------------------------------'
			user_input=raw_input('Turn on smoothing? [y,n]:')
			if user_input in yes:
				smooth=True
				for spec in spectra:
					flux=smoothBoxCar(flux)
			elif user_input in no:
				smooth=False
				flux=cp.deepcopy(spectrum[:,1])
			else:
				print user_input+': Not a valid entry. Back to command page.'
			print 'Smoothing:'+str(smooth)
			print '--------------------------------------------------------------------'
		elif user_input=='funcType':
			print '--------------------------------------------------------------------'
			print 'The current interpolation function is:',interpFunction
			print 'The options are: linear, nearest, zero, slinear,'
			print '                 quadratic, cubic'
			print '[If you dont know your stuff, you should read up on these'
			print 'on what these functions do at: scipy.interpolate.interp1d]'
			user_input=raw_input('Enter an interpolation function or (q,Q to skip):')
			if user_input in interpList:
				interpFunction=user_input
				print 'Changed interpolation function to:',interpFunction
			elif user_input=='q' or user_input=='Q':
				print 'The interpolation function is still:',interpFunction
			else:
				print user_input+': Not a valid entry. Back to command page.'
			print '--------------------------------------------------------------------'
		elif user_input=='write':
			print '--------------------------------------------------------------------'
			outfile=open(rootname+'.bpm.'+suffix,'w')
			for i in range(len(lam)):
				outfile.write(str(lam[i])+' '+str(flux[i])+' '+str(flux_err[i])+'\n')
			outfile.close()
			print 'New ASCII table written to file:'+rootname+'.bpm.'+suffix
			print 'NB: - Whatever is currently on the plot will be written to-file'
			print '    - bpm --> bad pixel mask'
			print 'Do with this file what you will!'
			print '--------------------------------------------------------------------'
		elif user_input=='regions':
			print '--------------------------------------------------------------------'
			print 'Here is the current list of regions you have removed:'
			print regionDict
			user_input=raw_input('Do you want to remove any regions? (y/n):')
			if user_input in yes:
				user_input=raw_input('Type the number you want to remove:')
				key=int(user_input)
				if key in regionDict.keys():
					print 'Removing region:',key,regionDict[key]
					#for the region they chose, need to copy the old spectrum stuff backover.
					indexes=[i for i,value in enumerate(lam) if value >= regionDict[key][0] and value <= regionDict[key][1]]
					for i in range(len(lam)):
						if i>=indexes[0] and i<=indexes[-1]:
							print lam[i],flux[i],'-->',spectrum[i,1]
							flux[i]=cp.deepcopy(spectrum[i,1])
					#delete from dictionary
					del regionDict[key]
					count-=1
					print 'Current regions:',regionDict
					print 'Updating figure.'
					graph.set_ydata(flux)
					scat.remove()
					scat=plt.scatter(lam,flux,s=10)
					plt.pause(0.01)
				elif key not in regionDict.keys():
					print 'Could not remove',key,'. It does not exist.'
			elif user_input in no:
				print 'okay.'
			else:
				print 'That wasnt an answer?, try again.'
			print '--------------------------------------------------------------------'
		else:
			print '***'
			print 'What chu talkin bout, that aint no command.'
			print '***'
	return
#------------------------------------------------------------------------------#


def smoothBoxCar(x,N=5):
	'''
	BoxCar smoothing function, optional
	'''
	boxcar=np.ones(N)
	return convolve(x, boxcar/boxcar.sum())
#------------------------------------------------------------------------------#

#
#START of program
#------------------------------------------------------------------------------#
#read in from command line
parser=argparse.ArgumentParser()
parser.add_argument('spec', type=str, help='/path/to/normalized/ASCII/spectrum')
parser.add_argument('-zem', type=float, default=0.0, help='redshift of target (If provided, will assume you want to shift to rest-frame).')
#parser.add_argument('-fig', type=str, default='spec_BPM.eps', help='The name of the output plot (default spec_BPM.eps)')
parser.add_argument('-kind', type=str, default='linear', help='Type of interpolation. i.e., linear, nearest, zero, slinear, quadratic, cubic. See: scipy.interpolate.interp1d.html')

kwargs=vars(parser.parse_args())
masking(**kwargs)
