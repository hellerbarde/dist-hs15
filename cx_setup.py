import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
}



executables = [
    Executable('spamfilter.py')
]

setup(name='spamfilter',
      version='0.1',
      description='Spam Filter for diskrete Stochastik',
      executables=executables,
      options=options
      )
