import DoorBot.Config as Config

# template strings for SCRIPTs and nginx
# uses .format()

API = r"""
#!/usr/bin/bash

base={base}
runtime=$base/venv/bin
host='127.0.0.1'
port=5000
workers=3

cd $base
source venv/bin/activate
$runtime/gunicorn DoorBot.API:app \
                --bind=$host:$port \
                --reload \
                --worker-class eventlet\
                -w $workers\
                --timeout=7200
            """
DOORLOCK = """
#!/usr/bin/bash

base={base}
runtime=${base}venv/bin/

cd $base

$runtime/python3 -m DoorBot.hw.doorLock
"""
DOORSWITCH = """
#!/usr/bin/bash

base={base}
runtime=${base}venv/bin/

cd $base

$runtime/python3 -m DoorBot.hw.doorSwitch
"""

RESET = """
#!/usr/bin/bash

base={base}
runtime=${base}venv/bin/

cd $base

$runtime/python3 -m DoorBot.hw.reset
"""
UPDATEIDCACHE = """
#!/usr/bin/bash

base={base}
runtime=${base}venv/bin/

cd $base

$runtime/python3 -m DoorBot.hw.updateIDCache
"""
READER = """
#!/usr/bin/bash

base={base}
runtime=${base}venv/bin/

cd $base

$runtime/python3 -m DoorBot.hw.reader
"""