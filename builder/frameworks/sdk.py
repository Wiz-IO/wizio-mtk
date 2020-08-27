
# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

from __future__ import print_function
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = "sdk"
module = platform + "-" + env.BoardConfig().get("build.core")
print(module)
m = __import__(module)       
globals()[module] = m
m.dev_init(env, platform)
#print( env.Dump() )
