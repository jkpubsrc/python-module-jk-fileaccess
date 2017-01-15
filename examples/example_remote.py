#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import sh

import jk_fileaccess




HOSTADDR="123.45.67.8"
USERNAME="someuser"
PASSWORD="somepassword"
REMOTEPATH="/some/remote/path"
FILESETNAME="SomeFileSet"

fs = jk_fileaccess.SshRemoteFileInterface("/tmp/SshRemoteFileInterface", HOSTADDR, 22, USERNAME, PASSWORD, REMOTEPATH, FILESETNAME, None)
print(str(fs.countDirs()) + " directories:")
for v in fs.getDirPathIterator():
	print("\t" + str(v))
print(str(fs.countFiles()) + " files:")
for v in fs.getFilePathIterator():
	print("\t" + str(v))

