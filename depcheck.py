# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from __future__ import print_function

print('Checking Dependency status:')
print(50*'-')

try:
    from osgeo import gdal, osr
except:
    print('gdal not installed!')
else:
    print('gdal \t\t - \t\tOK!')
finally:
    pass

try:
    import scipy
except:
    print('scipy not installed!')
else:
    print('scipy \t\t - \t\tOK!')
finally:
    pass

try:
    import matplotlib.pyplot as plt 
except:
    print('matplotlib not installed!')
else:
    print('matplotlib \t - \t\tOK!')
finally:
    pass

try:
    from mpl_toolkits.basemap import Basemap
except:
    print('basemap not installed!')
else:
    print('basemap \t - \t\tOK!')
finally:
    pass

try:
    import utide
except:
    print('utide not installed!')
else:
    print('utide \t\t - \t\tOK!')
finally:
    pass

try:
    import zipfile
except:
    print('zipfile not installed!')
else:
    print('zipfile \t - \t\tOK!')
finally:
    pass

try:
    import csv
except:
    print('csv not installed!')
else:
    print('csv \t\t - \t\tOK!')
finally:
    pass


try:
    import numpy as np 
except:
    print('numpy not installed!')
else:
    print('numpy \t\t - \t\tOK!')
finally:
    pass

try:
    from glob import glob
except:
    print('glob not installed!')
else:
    print('glob \t\t - \t\tOK!')
finally:
    pass


try:
    import gc
except:
    print('GC not installed!')
else:
    print('GC \t\t - \t\tOK!')
finally:
    pass

print('Done!')
print('Proceed to execute main.py')