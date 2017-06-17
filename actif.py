#! /usr/bin/env python3
import sys
## from actif_qt4 import main
from actif_qt import main

if len(sys.argv) > 1:
    main(a1=sys.argv[1], a2=sys.argv[2])
else:
    main()
    ## main(a1="actif.ini", a2="testing.ini")
