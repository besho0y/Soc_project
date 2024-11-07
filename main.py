from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *

put_text("learn python")

start_server(put_text,port=4567,debug=True)