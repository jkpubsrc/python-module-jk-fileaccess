#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pwd
import codecs
import os
import shutil
import sh

import jk_fileaccess





def testSharesRW(fs):
	print("testSharesRW")

	assert fs.isOpen
	assert not fs.isClosed

	# testing: writeAllDataToFile, readAllDataFromFile
	print("\ttesting: writeAllDataToFile, readAllDataFromFile")

	s = "abcdefghijklmnopqrstuvwxyz\nABCDEFGHIJKLMNOPQRSTUVWXYZ"
	fs.writeAllDataToFile("/test.txt", s.encode("utf-8"))
	s2 = fs.readAllDataFromFile("/test.txt")
	assert s == s2.decode("utf-8")

	# testing: uploadLocalFile, readAllDataFromFile
	print("\ttesting: uploadLocalFile, readAllDataFromFile")

	fs.uploadLocalFile("/etc/mime.types", "/test.txt", False)
	with codecs.open("/etc/mime.types") as f:
		s = f.read()
	mimeTypeText = fs.readAllDataFromFile("/test.txt")
	assert mimeTypeText.decode("utf-8") == s

	# testing: listDirectoryContentNames
	print("\ttesting: listDirectoryContentNames")

	names = fs.listDirectoryContentNames("/", bIncludeSubDirs = False, bIncludeFiles = True, bIncludeOthers = False)
	assert len(names) == 1
	assert names[0] == "test.txt"

	# testing: listDirectoryContent
	print("\ttesting: listDirectoryContent")

	entries = fs.listDirectoryContent("/", bIncludeSubDirs = False, bIncludeFiles = True, bIncludeOthers = False)
	assert len(entries) == 1
	for entry in entries:
		assert len(entry) == 7
		assert isinstance(entry[0], str)
		assert entry[0] == "test.txt"
		assert isinstance(entry[1], str)
		assert entry[1] == "f"
		assert isinstance(entry[2], int)
		assert isinstance(entry[3], int)
		assert isinstance(entry[4], int)
		assert isinstance(entry[5], int)
		assert isinstance(entry[6], float)

	# testing: deleteFile
	print("\ttesting: deleteFile")

	fs.deleteFile("/test.txt")
	names = fs.listDirectoryContentNames("/", bIncludeSubDirs = False, bIncludeFiles = True, bIncludeOthers = False)
	assert len(names) == 0

	# testing: createDirectory
	print("\ttesting: createDirectory")

	names = fs.listDirectoryContentNames("/", bIncludeSubDirs = True, bIncludeFiles = False, bIncludeOthers = False)
	assert len(names) > 0
	bFound = False
	for name in names:
		if name == "testdir":
			fs.deleteEmptyDirectory("/testdir")

	fs.createDirectory("/testdir")
	names = fs.listDirectoryContentNames("/", bIncludeSubDirs = True, bIncludeFiles = False, bIncludeOthers = False)
	assert len(names) > 0
	bFound = False
	for name in names:
		if name == "testdir":
			bFound = True
			names = fs.listDirectoryContentNames("/testdir", bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = False)
			assert len(names) == 0
	assert bFound

	# testing: listDirectoryContent
	print("\ttesting: listDirectoryContent")

	entries = fs.listDirectoryContent("/", bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = False)
	assert len(entries) > 0
	bFound = False
	for entry in entries:
		if entry[0] == "testdir":
			assert len(entry) == 7
			assert isinstance(entry[0], str)
			assert entry[0] == "testdir"
			assert isinstance(entry[1], str)
			assert entry[1] == "d"
			assert isinstance(entry[2], int)
			assert isinstance(entry[3], int)
			assert isinstance(entry[4], int)
			assert isinstance(entry[5], type(None))
			assert isinstance(entry[6], type(None))
			break

	# testing: deleteEmptyDirectory
	print("\ttesting: deleteEmptyDirectory")

	fs.deleteEmptyDirectory("/testdir")
	names = fs.listDirectoryContentNames("/", bIncludeSubDirs = True, bIncludeFiles = False, bIncludeOthers = False)
	assert len(names) > 0
	bFound = False
	for name in names:
		if name == "testdir":
			bFound = True
	assert not bFound

	print("\tDone.")
#



def testSharesRO(fs):
	print("testSharesRO")

	assert fs.isOpen
	assert not fs.isClosed

	# testing: listDirectoryContent
	print("\ttesting: listDirectoryContent")

	entries = fs.listDirectoryContent("/", bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = False)
	for entry in entries:
		print("\t\t:: " + entry[1] + " :: " + entry[0])

	print("\tDone.")
#






#### Test LocalShare

"""
TEMP_DIR = "/tmp/jk_fileaccess-test"

if not os.path.isdir(TEMP_DIR):
	os.mkdir(TEMP_DIR)
else:
	shutil.rmtree(TEMP_DIR)
	os.mkdir(TEMP_DIR)

fs = jk_fileaccess.LocalShare(TEMP_DIR)
testSharesRO(fs)
testSharesRW(fs)
"""




#userName = "p-dataarch"
#sharePath = "/home/dataarch/nfs-share"

userName = "p-asymenc"
sharePath = "/home/dataarch/nfs-share-asymenc"

(pw_name, pw_passwd, pw_uid, pw_gid, pw_gecos, pw_dir, pw_shell) = pwd.getpwnam(userName)
print("Using UID " + str(pw_uid))

os.seteuid(pw_uid)

fs = jk_fileaccess.LocalShare(sharePath)
#testSharesRO(fs)
#testSharesRW(fs)
fs.performSpeedTest()

os.seteuid(0)




#### Test SftpShare

# fs = jk_fileaccess.SftpShare(tempDirPath, hostName, port, userName, password, baseDir)
# testShares(fs)




#### Test CifsShare

# c = jk_fileaccess.CifsClient(serverIPAddress, userName, password)
# fs = c.openShare(shareName)
# testShares(fs)








