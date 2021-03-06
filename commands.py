#!/bin/python

import subprocess
import shlex

def run_command(command, pipe_in=''):
    '''
    Run command and return its output by optionally piping in pipe_in.
    Same as
        command < pipe_in.txt
    where pipe_in.txt contains pipe_in.  If no pipe_in is
    specified, or pipe_in is '', then just run the command
    and return its output.
    '''
    if pipe_in == '':
        process = subprocess.Popen(shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout
    else:
        # See http://stackoverflow.com/a/165662/3422337
        process = subprocess.Popen(shlex.split(command),
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output = process.communicate(input=pipe_in)[0]
        return output

def write_to_filepath(contents, filepath):
    with open(filepath, 'w') as f:
        f.write(contents)

