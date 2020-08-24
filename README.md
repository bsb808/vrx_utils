# vrx_utils
Utilities for the VRX project - bits that aren't appropriate for the main repos.


## How to run an experiment


### Configuration


### Execution flow

See `run_experiments.py` which does the following...

For each experiment...

1. Generates a world.xacro file
2. Process xacro to generate .world file
3. Start experiment
   1. Start core and rosbag record
   2. Call launch file with a timeout - world file is an argument.
4. When done - shut things down.
