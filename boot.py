# boot.py -- run on boot-up
import gc
gc.collect()

import os
try:
    import machine
    sd = machine.SDCard()
    os.mount(sd, '/sd')
except:
    pass

try:
    import webrepl
    webrepl.start(password='espelt2024')
except:
    pass
