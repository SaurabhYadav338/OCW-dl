import os

def sanitize_fs_element(name):
    name = "".join(x for x in name if (x.isalnum() or x in "._- "))
    while name[0] in ['.', ' ']:
        name = name[1:]
    while name[-1] in ['.', ' ']:
        name = name[:-1]
    if len(name) is 0:
        name = 'new'
    return name