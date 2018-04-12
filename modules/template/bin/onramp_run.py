#!/usr/bin/env python

#
# Curriculum Module Run Script
# - Run once per run of the module by a user
# - Run inside job submission. So in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from subprocess import call
from configobj import ConfigObj

#
# Read the configobj values
#
# This will always be the name of the file, so fine to hardcode here
conf_file = "onramp_runparams.cfg"
# Already validated the file in our onramp_preprocess.py script - no need to do it again
config    = ConfigObj(conf_file)

#
# Load any modules for running
#   - need to load mpi module on flux
#
try:
    rtn = check_call("module load mpi")
except CalledProcessError as e:
    print "Error loading module.\nError: %s" % e
    sys.exit(-1)


#
# Run my program
#
os.chdir('src')
call(['mpirun', '-np', config['onramp']['np'], 'hello', config['hello']['name']])


# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
