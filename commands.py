#!/bin/python

import subprocess
import shlex

def run_command(command, pipe_in):
    '''
    Run command by piping in pipe_in.  Same as
        command < pipe_in.txt
    where pipe_in.txt contains pipe_in.
    '''
    if pipe_in == '':
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = process.communicate(input=pipe_in)[0]
        return output
    else:
        return output

def write_to_filepath(contents, filepath):
    with open(filepath, 'w') as f:
        f.write(contents)

