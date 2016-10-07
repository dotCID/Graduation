#!/usr/bin/python

# @author https://github.com/JoshData :
# Given a stream of accelerometer data on a device moving
# rhythmically (i.e. to a beat) compute the frequency at
# which the device is moving, the force of movement, and
# predict the time of the next beat.
#
# For instance, if you are fist pumping, it will compute
# the tempo of the music that you are following (in Hertz)
# and the time of the next beat.
#
# The technique is based on Singular Value Decomposition (to
# convert 3D motion data to a 1D stream) and Fast Fourier
# Transform (to compute the frequency space).
#
# Reads a stream of "x,y,z" accelerometer data coming in
# on standard input. If getting data via a TCP socket, say
# on port 18250 like the Accelerometer Mouse app does, run
# this script by piping data from socat:
#
#    socat TCP-LISTEN:18250,fork - | python beat.py
#
# Inspired by @TJL's tweet.

# @author https://github.com/dotCID :
# Adapted for use during my graduation project. 
# Most additions/alterations are marked with "MCW"

# MCW: make it possible to import from parent directory:
import sys
sys.path.insert(0,'..')


# MCW: Change terminal window header for easier identification of contents
sys.stdout.write("\x1b]2;Sensors/beatDetect.py\x07")

import sys
import numpy
import numpy.linalg
import scipy, scipy.fftpack
from datetime import datetime
from time import sleep

from globalVars import CHANNEL_BEATDATA
from globalVars import CHANNEL_IMU_RAWACCEL

from globalVars import ENERGY_AVG_LENGTH
import time, zmq

# Configuration: How often should we re-estimate the sample
# frequency (based on how fast data is coming in, as long
# as we can keep up with it!). This is a number of samples.
sample_time_every = 20

# How many samples should we compute the FFT over? A longer
# history means it takes longer to shift to new rhythms, but
# the frequency will be more accurate because it has a larger
# sample size to be computed from.
sample_history_size = 150

# How often should we readjust the beat detection's zero point?
beat_phase_every = 10

# Some ongoing state. The current estimate of the sample
# frequency:
sample_freq = None

# And the current sample number, incremented consecutively:
current_sample_num = 0

# Buffers
history_time = [] # current time every sample_time_every samples
history_acc = [] # last sample_history_size accelerometer values
history_f0 = [0.0 for i in xrange(4)] # computed frequencies
history_phase = [0.0 for i in xrange(10)] # computed phases

# For predicting beats, the last beat predicted so that we don't
# predict another beat again right away.
phase_at_zero = 0
last_beat = 0

# MCW: Set up ZMQ publishing:
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(CHANNEL_BEATDATA)

## ZMQ Raw Accel channel - Raw accelleration from the IMU
ra_context = zmq.Context()
rawAccelChannel = ra_context.socket(zmq.SUB)
rawAccelChannel.setsockopt(zmq.CONFLATE, 1 )
rawAccelChannel.setsockopt(zmq.SUBSCRIBE, '')
rawAccelChannel.connect(CHANNEL_IMU_RAWACCEL)

accelPoller = zmq.Poller()
accelPoller.register(rawAccelChannel, zmq.POLLIN)

# MCW: Arduino-style millis() function for timekeeping
millis = lambda: int(round(time.time() * 1000))

# MCW: Simple BPM tracking list
BPM = 0.0
beatTimes = range(10)

# MCW: Threshold above which beats 'count':
S_THRESHOLD = 1.0

# MCW: Average s0 over past measurements
s0_list = [40]*ENERGY_AVG_LENGTH
s0_avg = 40.0

# MCW: BPM computation
def computeBPM():
    '''
    @author MCW
    Takes the average BPM over n-1 time stamps
    '''
    global beatTimes
    diff = range(len(beatTimes)-1)
    for i in range(len(beatTimes)-1):
        diff[i] = beatTimes[i+1] - beatTimes[i]
    
    t = sum(diff)
    
    if t != 0:
        avgDiff = t / float(len(diff))
        _bpm = 60000.0 / avgDiff
    else:
        _bpm = 0
    
    return _bpm
    
def listShift(ls, newEntry):
    '''
    @author MCW
    Shifts the contents of a list and adds the new entry to the end
    '''
    for i in range(len(ls)-1):
        ls[i] = ls[i+1]
    ls[-1] = newEntry
    
    return ls


print "--------------\nBeat.py is now running.\n--------------\n"

while True:    

    # read from ZMQ; only continue if there is new data to process
    if len(accelPoller.poll(0)) is not 0:
        rawAccelData = rawAccelChannel.recv_json()
    
        # Convert JSON to list and lose the 't'
        line = [ rawAccelData['x'], rawAccelData['y'], rawAccelData['z'] ]
        
        # Get the accelerometer data and put it into a history array.
        vector = [float(f) for f in line[0:3]]
        history_acc.append(vector)
        if len(history_acc) > sample_history_size: history_acc.pop(0)
        
        # Estimate the sample frequency every 10 samples by the
        # number of samples acquired divided by the time elapsed.
        # Make sure that this is executed on the first iteration.
        if (current_sample_num % sample_time_every) == 0:
            history_time.append(datetime.now())
            if len(history_time) > 10: history_time.pop(0)
            ts = (history_time[-1]-history_time[0]).total_seconds()
            if ts == 0.0: continue
            sample_freq = sample_time_every * float(len(history_time)) / ts
        current_sample_num += 1
        if sample_freq == 0.0: continue # not yet computed

        # There must be something like a 3D FFT, but to use the
        # normal FFT we must compute a single value, not a vector,
        # at each time in the history. We need a method to convert
        # the 3D history data into 1D data.
        
        # Let's assume that the device is moving back and forth
        # along a line in 3D space (i.e. not a circular motion).
        # Then the best history to pass into the FFT will be the
        # devices position (accelerometer reading) along that line,
        # i.e. a projection of the position vector onto the line.
        # Call that line the primary direction of motion.
        
        # To compute the primary direction of motion, we will use
        # my friend the Singular Value Decomposition, which is a
        # technique for dimensionality reduction (e.g. 3D to 1D).
        # We pass the SVD the history array, and it computes three
        # (because the original vectors are 3D) new vectors that
        # when linearly combined best approximate the original
        # matrix of history vectors. The new vectors are ordered,
        # and the first is the vector that explains most of the
        # original history matrix. Thus, it is the primary direction
        # of motion.
        
        # In the language of FFTs, there is a DC component to the
        # accelerometer data. At rest, the accelerometer reports the
        # force of gravity. We must subtract the DC component before
        # using SVD, or else it will get in the way.
        #
        # Subtract off the mean value on each axis from the history.
        m = [0, 0, 0]
        for i in xrange(3): m[i] = numpy.mean([h[i] for h in history_acc])
        m = numpy.array(m)
        history = [h-m for h in history_acc]
        
        # Compute the SVD.
        u, s, vT = numpy.linalg.svd(history)
        
        # vT[0]  - the primary direction of motion (vector norm is 1.0)
        # u[:,0] - the coordinate on the 'primary direction of motion'
        #          axis for each point in the history (vector norm is 1.0)
        # s[0]   - a scale factor that when applied to u and vT gives back
        #          the actual magnitudes of the acceleration over the history
        #          (so it is a sort of average absolute acceleration over
        #          the history).
        
        history_acc1d = u[:,0]
        
        # Compute the fundamental frequency of the 1D history data by passing
        # the 1D accelerometer values into a Fast Fourier Transform. This
        # gives a power level at a range of frequency components in the signal.
        FFT = scipy.fft(history_acc1d)
        
        # The FFT power values are complex numbers at first. Take abs to get
        # a real power. Also, weight low frequencies more highly since there
        # may be high-frequency energy especially at multiples of the fundamental
        # frequency. This is a made up exponential decay that seems to work well.
        FFTpower = abs(FFT)
        for i in xrange(len(FFT)):
            FFTpower[i] *= 2**(-i/float(len(history_acc1d)))
        
        # Find the peak of the power spectrum, and the frequency that corresponds
        # to that power.
        f0_i = numpy.argmax(FFTpower[1:]) + 1 # skip the DC component of the signal
        freqs = scipy.fftpack.fftfreq(len(history_acc1d), 1.0/sample_freq)
        f0 = abs(freqs[f0_i]) # FFT gives negative frequencies? Hmmm.
        
        # Add the computed frequency to a short history and smooth the frequency
        # by taking the mean over the history.
        history_f0.append(f0)
        history_f0.pop(0)
        f0 = numpy.mean(history_f0)
        
        # MCW: add s0 to the list, compute average
        s0_list = listShift(s0_list, s[0])
        s0_avg = sum(s0_list) / len(s0_list)

        msg = {
                    't'      : millis(),
                    'f0'     : f0,
                    's0'     : s[0],
                    's0_avg' : s0_avg,
                    'bpm'    : BPM,
                    'beat'   : False
                }
        
        samples_per_beat = int(round(sample_freq / f0))
        if (current_sample_num % beat_phase_every) == 0:
            # We can also predict the next beat by getting the phase of the
            # beat at the current time and projecting forward based on the
            # computed period, i.e. the inverse of the fundamental frequency.
        
            # This gets the current phase in radians in the range [-pi,pi].
            phase = numpy.angle(FFT[f0_i])
            
            # If there are X samples in a beat, what phase was sample 0
            # in the range of [0,X)?
            phase_now = int(round( (phase + numpy.pi/2)/(2*numpy.pi) * samples_per_beat ))
            phase_at_zero = (phase_now - current_sample_num) % samples_per_beat
            
            # The phase is very wobbly over time, so we need to smooth it.
            history_phase.append(phase_at_zero)
            history_phase.pop(0)
            phase_at_zero = int(numpy.median(history_phase))
        
        # Should we beat now? Just prevent two beats close together.
        if samples_per_beat is not 0:
            if (current_sample_num % samples_per_beat) == 0 \
              and current_sample_num > last_beat + .8*samples_per_beat \
              and s[0] > S_THRESHOLD:

                beatTimes = listShift(beatTimes, millis())
                BPM = computeBPM()            
                        
                msg = {
                    't'      : millis(),
                    'f0'     : f0,
                    's0'     : s[0],
                    's0_avg' : s0_avg,
                    'bpm'    : BPM,
                    'beat'   : True
                }
                last_beat = current_sample_num
            
        # MCW: Send message
        print "Sent beatData: ", 
        print msg
        socket.send_json(msg)
