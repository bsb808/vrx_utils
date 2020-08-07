#!/usr/bin/env python
import os
import sys
import time
import subprocess
from argparse import ArgumentParser

''' 
Generate monochromatic world file
'''

if __name__ == '__main__':
    # Create a command line argument parser
    parser = ArgumentParser(description="Generates mono world file")
    parser.add_argument('--amplitude', type=float, default=0.0,
                        help="Wave amplitude [m]")
    parser.add_argument('--period', type=float, default=10.0,
                        help="Wave period [s]")
    parser.add_argument('--direction_x', type=float, default=1.0,
                        help="Wave direction, x coordinate")
    parser.add_argument('--direction_y', type=float, default=0.0,
                        help="Wave direction, y coordinate")
    args = parser.parse_args()

    
    # File names
    fname_base =  "./mono_worlds/mono_world_a_%0.1f_p_%0.2f_x_%0.2f_y_%0.2f"%(args.amplitude,
                                                                args.period,
                                                                args.direction_x,
                                                                args.direction_y)
    fname_bag = fname_base+'.bag'
    fname_world = fname_base+'.world'
    fname_world_xacro = fname_world + ".xacro"

    ### Generate world.xacro file
    # Create parameter line
    xacro_args = '<xacro:ocean_waves_mono amplitude="%0.1f" period="%0.2f" direction_x="%0.2f" direction_y="%0.2f"/>\n'%(args.amplitude, args.period, args.direction_x, args.direction_y)

    # Concatenate header - line - footer
    head = open('ocean_mono_param.world.xacro.head').read()
    foot = open('ocean_mono_param.world.xacro.foot').read()
    f = open(fname_world_xacro,'w')
    f.write(head)
    f.write(xacro_args)
    f.write(foot)
    f.close()

    print "Wrote <%s>"%fname_world_xacro

    ### Process xacro to generate world file
    p = subprocess.Popen(['xacro',fname_world_xacro], stdout=subprocess.PIPE)
    output, err = p.communicate()
    f = open(fname_world,'w')
    f.write(output)
    f.close()
    print "Wrote <%s>"%fname_world

    ### Start roscore and bag file
    print "Start Core"
    core = subprocess.Popen(['roscore'])
    time.sleep(2)
    print ("Starting bag file <%s>"%fname_bag)
    bagger = subprocess.Popen(['rosbag','record','--all',
                               '--output-name=%s'%fname_bag])

    ### Start simulation with world file
    world = os.path.abspath(fname_world)
    print 'Starting world: <%s>'%world
    cmdlist = ['roslaunch','vrx_utils','ocean_mono_timed.launch',
                          'world:=%s'%world,
                          'x:=0',
                          'y:=0',
                          'timeout:=10.0']
    print "Command: <%s>"%(' '.join(cmdlist))
    p = subprocess.Popen(['roslaunch','vrx_utils','ocean_mono_timed.launch'],
                         stdout=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err

    # Kill
    print("Shutting down...")

    bagger.kill()
    core.kill()

          

                     
    

