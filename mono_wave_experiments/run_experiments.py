#!/usr/bin/env python
import os
import sys
import time
import subprocess
import math
from datetime import datetime
import numpy as np

from argparse import ArgumentParser

''' 

'''

def run_mono_experiment(exp_dir,amplitude=0.0, period=10.0,
                        direction_x=1.0, direction_y=0.0,
                        x = 0.0, y = 0.0, Y = 0.0, timeout = 60.0,
                        gui='true',
                        thrust=None):
    l = 0.0
    r = 0.0
    if not(thrust is None):
        l = thrust[0]
        r = thrust[1]
    
    
                        
    exp_str = 'a_%0.2f_p_%0.2f_x_%0.2f_y_%0.2f_Y_%0.3f_left_%0.2f_right_%0.2f_'%(amplitude,
                                                                                period,
                                                                                direction_x,
                                                                                direction_y,
                                                                                Y,
                                                                                l, r)
    # File names
    #fname_base =  "./experiments/mono_world_%s"%exp_str
    fname_base =  os.path.join(exp_dir,"mono_world_%s"%exp_str)
    fname_bag = fname_base+'.bag'
    fname_world = fname_base+'.world'
    fname_world_xacro = fname_world + ".xacro"

    ### Generate world.xacro file
    # Create parameter line
    xacro_args = '<xacro:ocean_waves_mono amplitude="%0.2f" period="%0.2f" direction_x="%0.2f" direction_y="%0.2f"/>\n'%(amplitude, period, direction_x, direction_y)
    
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
                               '--output-name=%s'%fname_bag,
                               '__name:=bagger'])

    # If thee is thrust commands, send 'em
    if not(thrust is None):
        
        left = subprocess.Popen(['rostopic','pub','-r','10',
                                 '/wamv/thrusters/left_thrust_cmd','std_msgs/Float32',
                                 str(thrust[0]),
                                 '__name:=left'])
        right = subprocess.Popen(['rostopic','pub','-r','10',
                                 '/wamv/thrusters/right_thrust_cmd','std_msgs/Float32',
                                  str(thrust[1]),
                                  '__name:=right'])
        
    ### Start simulation with world file
    world = os.path.abspath(fname_world)
    print 'Starting world: <%s>'%world
    cmdlist = ['roslaunch','vrx_utils','ocean_mono_timed.launch',
               'world:=%s'%world,
               'x:=0',
               'y:=0',
               'Y:=%.3f'%Y,
               'timeout:=%.1f'%timeout,
               'gui:=%s'%gui]
    print "Command: <%s>"%(' '.join(cmdlist))

    p = subprocess.Popen(cmdlist,
                         stdout=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err
    '''
    print('Sleeping')
    time.sleep(20)
    '''

    # Kill
    print("Shutting down...")

    #bagger.kill()
    #outs, errs = bagger.communicate()

    node_hitlist = ['/bagger','/left','/right']
    for node in node_hitlist:
        cmdlist = ['rosnode','kill',node]
        print "Command: <%s>"%(' '.join(cmdlist))
        p = subprocess.Popen(cmdlist,
                             stdout=subprocess.PIPE)
        output, err = p.communicate()

    # Run kill all scrip
    for rproc in [bagger, core]:
        '''while rproc.poll() is None:
           
            rproc.kill() #terminate()
            time.sleep(1.0)
        '''

        print ("Killing bagger then core")
        rproc.kill()
        outs, errs = rproc.communicate()        
        print "Killed"
    
    print("Exiting...")
    time.sleep(1.0)

    # Run kill all script
    cmdlist = ['./kill_todo.sh']
    print "Command: <%s>"%(' '.join(cmdlist))
    p = subprocess.Popen(cmdlist,
                         stdout=subprocess.PIPE)
    output, err = p.communicate()


def make_experimentdir(logdir, exp_label):
    '''
    Make new logging directory 
    - increment number to find a unique directory
    '''

    # Add date str
    now = datetime.now() # current date and time
    datestr = now.strftime("%Y_%m_%d")

    n = 0
    exp_dir = os.path.join(logdir,'%s_%s_%03d'%(datestr,exp_label,n))
    while os.path.isdir(exp_dir):
        print "Can't overwrite <%s>, incrementing."%exp_dir
        exp_dir = os.path.join(logdir,'%s_%s_%03d'%(datestr,exp_label,n))
        n+=1
    os.mkdir(exp_dir)
    print ('Logging data to <%s>'%exp_dir)
    return exp_dir

if __name__ == '__main__':

    # Setup destination and label
    logdir = '/home/bsb/data'


    # Mono experiments, seakeeping
    for label, yaw in zip(['head_seas', 'beam_seas'],
                          [0.0, math.pi/2.0]):
        
        exp_label = label
        exp_dir = make_experimentdir(logdir, exp_label)
        '''
        amplitudes = [0.00,
                      0.21,
                      0.34,
                      0.44,
                      0.50,
                      0.70,
                      0.93,
                      1.05,
                      1.22,
                      1.52,
                      1.83]
        '''
        period = 6.0
        amplitudes = np.linspace(0.0, 1.0, 11)
        for a, i in zip(amplitudes, range(len(amplitudes))):
            print"****************************************"
            print" Running %d of %d "%(i,len(amplitudes))
            for r in range(10):
                print"****************************************"

            run_mono_experiment(exp_dir, gui='false',
                                amplitude=a, period=period, Y=yaw)


    '''
    # Manuevering experiments
    exp_label = 'manuevering'
    exp_dir = make_experimentdir(logdir, exp_label)

    mag = 0.75
    thrusts = [ (1.0, 0.95),
                (1.0, 0.90),
                (1.0, 0.85),
                (1.0, 0.80),
                (1.0, 0.75)]
    for t in thrusts:
        l,r  = t

        left = l/(math.sqrt(l**2 + r**2))*mag
        right = r/(math.sqrt(l**2 + r**2))*mag
    
        run_mono_experiment(exp_dir,
                            amplitude=0, gui='false', thrust=(left, right))
    
    '''
