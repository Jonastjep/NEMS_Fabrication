import gdsfactory as gf
import HBAR_lib as hbar
from itertools import zip_longest

from gdsfactory.generic_tech import LAYER


out = gf.Component()

a = hbar.HBAR_coupling_single_conn()


out << a
out.show()