import re
from pprint import pprint as pp

import pyRofex
tickers = ['GGAL', 'PAMP', 'YPF', 'DO']
progs = [re.compile(f'^{each}[A-Z][a-z][a-z]2.$') for each in tickers]


pyRofex.initialize(user="pepieroni5584",
                   password="smstzM4#",
                   account="REM5584",
                   environment=pyRofex.Environment.REMARKET)

# all_instr = pyRofex.get_all_instruments()
all_instr = pyRofex.get_detailed_instruments()
for instr in all_instr['instruments']:
    for prog in progs:
        if prog.match(instr['instrumentId']['symbol']):
            # pp(instr['instrumentId']['symbol'])
            pp(instr)