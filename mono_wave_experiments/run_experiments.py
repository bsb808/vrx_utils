#!/usr/bin/env python
import os
import sys
import time
import subprocess
from argparse import ArgumentParser

''' 

'''

def run_experiment(amplitude=0.0, period=10.0,
                   direction_x=1.0, direction_y=0.0,
                   x = 0.0, y = 0.0, Y = 0.0, timeout = 10.0):

    exp_str = 'a_%0.1f_p_%0.2f_x_%0.2f_y_%0.2f_Y_%0.3f'%(amplitude,
                                                         period,
                                                         direction_x,
                                                         direction_y,
                                                         Y)
    # File names
    fname_base =  "./experiments/mono_world_%s"%exp_str
    fname_bag = fname_base+'.bag'
    fname_world = fname_base+'.world'
    fname_world_xacro = fname_world + ".xacro"

    ### Generate world.xacro file
    # Create parameter line
    xacro_args = '<xacro:ocean_waves_mono amplitude="%0.1f" period="%0.2f" direction_x="%0.2f" direction_y="%0.2f"/>\n'%(amplitude, period, direction_x, direction_y)
    
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

    p = subprocess.Popen(cmdlist,
                         stdout=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err

    # Kill
    print("Shutting down...")

    #bagger.kill()
    #outs, errs = bagger.communicate()
    bagger.terminate()
    while bagger.poll() is None:
        print ("Terminating bag record")
        bagger.terminate()
    
    core.kill()
    outs, errs = core.communicate()

    print("Exiting...")


if __name__ == '__main__':

    run_experiment()


          

                     
    

