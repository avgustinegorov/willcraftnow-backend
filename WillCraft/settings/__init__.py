import os

import environ
from termcolor import colored

from .analytics import *
from .auth import *
from .base import *
from .cors import *
from .databases import *
from .email import *
from .internationalization import *
from .pricing import *
from .ssl import *
from .stripe import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    STAGE=(str, "LOCAL"),
)
# reading .env file
environ.Env.read_env()

if env("STAGE") == "LOCAL":
    from .silk import *

if env("STAGE") == "LOCAL":
    from .static import *

if env("STAGE") != "LOCAL":
    from .aws import *

try:
    from .local import *
except:
    pass


# for name, value in globals().copy().items():
#     if value.__class__.__name__ == "module":
#         message = f"Imported {name.upper()} Settings Module"
#         print(colored(message, "red"))
#         print(colored(value, "red"))
#     else:
#         print(name, value)
