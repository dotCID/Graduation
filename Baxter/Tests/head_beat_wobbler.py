#!/usr/bin/env python

# Copyright (c) 2013-2015, Rethink Robotics
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Rethink Robotics nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

### @author Marien Wolthuis ###
## This script is intended to wobble the head to a "beat" ##
## It is a modified version of the head_wobbler.py script ##
## from the Baxter SDK                      ##
import argparse

import rospy

import baxter_interface

from baxter_interface import CHECK_VERSION


class Wobbler(object):

    def __init__(self):
        """
        'Wobbles' the head
        """
        self._done = False
        self._head = baxter_interface.Head()

        # verify robot is enabled
        print("Getting robot state... ")
        self._rs = baxter_interface.RobotEnable(CHECK_VERSION)
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")
        self._rs.enable()
        print("Running. Ctrl-c to quit")

    def clean_shutdown(self):
        """
        Exits example cleanly by moving head to neutral position and
        maintaining start state
        """
        print("\nExiting wobble...")
        if self._done:
            self.set_neutral()
        if not self._init_state and self._rs.state().enabled:
            print("Disabling robot...")
            self._rs.disable()

    def set_neutral(self):
        """
        Sets the head back into a neutral pose
        """
        self._head.set_pan(0.0)

    def wobble_beat(self, beat, duration):
        """
        @type  beat int
        @param beat beats per minute
        @type  duration int
        @param duration execution total duration in seconds
        """

        
        self.set_neutral()
        """
        Performs the wobbling
        """
        print('beat: '+str(beat))
        print('duration: '+str(duration))
        
        wobble_rate = rospy.Rate(beat/60.0)  # rate of the wobble
        start = rospy.get_time()
        angle = 0.0

        while not rospy.is_shutdown() and (rospy.get_time() - start < duration) :
            angle = 0.25
            self._head.set_pan(angle, speed=30)
            print(str(rospy.get_time()-start)+': right')
            wobble_rate.sleep()

            angle = -0.25
            self._head.set_pan(angle, speed=30)
            print(str(rospy.get_time()-start)+': left')
            wobble_rate.sleep()

        self._done = True
        rospy.signal_shutdown("Beat wobble finished.")


def main():
    parser = argparse.ArgumentParser(description='Wobble the head to a specified beat.')
    parser.add_argument('--beat', '-b', type=int, default=30, help='The beats per minute at which to wobble')
    parser.add_argument('--duration', '-d', type=int, default=10, help='The duration of the action in seconds')

    args = parser.parse_args()

    print(args)
    
    print("Initializing node... ")
    rospy.init_node("head_beat_wobbler")

    wobbler = Wobbler()
    rospy.on_shutdown(wobbler.clean_shutdown)
    print("Wobbling... ")
    wobbler.wobble_beat(args.beat, args.duration)
    print("Done.")

if __name__ == '__main__':
    main()
