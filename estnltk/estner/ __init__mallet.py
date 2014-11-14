import os
import sys


# Add java dependencies to the path:

from estner import settings
java_bin = os.path.join(settings.PATH, "bin")
java_lib_dir = os.path.join(settings.PATH, "lib")
sys.path.append(java_bin)
sys.stderr.write('java_bin: ' + java_bin + '\n');
sys.stderr.write('java_lib_dir: ' + java_lib_dir + '\n');
for jar in os.listdir(java_lib_dir):
    sys.path.append(os.path.join(java_lib_dir, jar))
