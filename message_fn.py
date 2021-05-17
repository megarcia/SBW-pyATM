# pylint: disable=R1711
"""
Python script "message_fn.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2019 by Matthew Garcia
"""


import sys


def message(char_string=''):
    """Print a string to the terminal and flush the buffer."""
    print(char_string)
    sys.stdout.flush()
    return

# end message_fn.py
