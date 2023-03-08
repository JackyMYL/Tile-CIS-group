#!/usr/bin/env python

import os, sys
os.chdir(os.getenv('TUCS','.'))
from src.region import *

#constructATLAS().Print()

constructATLAS().Print(3)
