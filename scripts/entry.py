import os, sys
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base, "..", "src"))
from rozetka.main import main
raise SystemExit(main())
