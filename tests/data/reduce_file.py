import random
import os
import sys

batch_size = 23
lineno = 0

with open("pak.data") as fh:
    flag_exit = False
    while True:
        lines = []
        for i in range(batch_size):
            line = fh.readline()
            if not line:
                flag_exit = True
                break
            lines.append(line)
            lineno += 1
    
        if not lines:
            exit()
        selection = random.randint(0, len(lines)-1)
        try:
            sys.stdout.write(lines[selection])
        except Exception as e:
            print((len(lines), selection))
            exit()

        sys.stderr.write(str(lineno)+"\n")
        if flag_exit:
            exit()
