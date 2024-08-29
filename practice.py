<<<<<<< HEAD
import tensorflow as tf
import keras
import sys

print("TensorFlow version:", tf.__version__)
print("Keras version:", keras.__version__)

print(sys.version)
=======
import os

# 논리적 CPU 코어 수 확인
logical_cores = os.cpu_count()
print(f"논리적 CPU 코어 수: {logical_cores}")

# 물리적 CPU 코어 수 확인 (Linux 및 macOS)
try:
    physical_cores = len(set(os.sched_getaffinity(0)))
    print(f"물리적 CPU 코어 수: {physical_cores}")
except AttributeError:
    print("물리적 CPU 코어 수를 확인할 수 없습니다. (Windows 또는 지원되지 않는 플랫폼)")
>>>>>>> 4c273fa1deac2421c828016d66317a2cd474bc9d
