import sys
import math
def funcX(a):
    return (- 1 - math.sqrt(a)) / (-1 + math.sqrt(a))

a = float(sys.argv[1])
ans = math.atan2(1, funcX(a)) * 180/math.pi
print("alpha: {}, stream angle (degrees): {}".format(a, ans))
