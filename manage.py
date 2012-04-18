#!/usr/bin/env python
from django.core.management import execute_manager

import imp
import sys

try:
    imp.find_module('settings')
except ImportError:
    import sys
    sys.stderr.write('Error: Cannot import settings file from settings directory.\n')
    sys.exit(1)

try:
    from settings import active as settings
    sys.stdout.write('** Using DEVELOPMENT settings\n')
except ImportError:
    from settings import production as settings
    sys.stdout.write('** Using PRODUCTION settings\n')

if __name__ == "__main__":
    execute_manager(settings)