#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import sh

import jk_fileaccess




fs = jk_fileaccess.LocalFileInterface("../testdata", "testA", None)
print(str(fs.countDirs()) + " directories:")
for v in fs.getDirPathIterator():
	print("\t" + str(v))
print(str(fs.countFiles()) + " files:")
for v in fs.getFilePathIterator():
	print("\t" + str(v))






