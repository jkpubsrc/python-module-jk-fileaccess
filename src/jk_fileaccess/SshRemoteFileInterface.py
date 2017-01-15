#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import traceback
import sys
import pprint							# see: https://docs.python.org/2/library/pprint.html
from datetime import datetime
import gzip

import pysftp							# see: http://pysftp.readthedocs.io/en/release_0.2.9/
import sh

from jk_temporary import *

from .AbstractFileInterface import AbstractFileInterface





class SshRemoteFileInterface(AbstractFileInterface):

	def __init__(self, tempDirPath, hostname, port, userName, password, rootDirPath, fileSetName, filePathFilter):
		if not os.path.exists(tempDirPath):
			os.mkdir(tempDirPath)

		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None
		self.__con = pysftp.Connection(hostname, username=userName, password=password, cnopts=cnopts)

		self.__tempDir = TempDir(tempDirPath, 'sftp-', None, None, 32, 0o600, 0o700)
		self.__tempDir.clear()

		self.__filePaths = []
		self.__dirPaths = []
		self.__fileSizes = []
		self.__timeStamps = []

		# change into target directory
		self.__con.chdir(rootDirPath)

		# download and parse file index
		path = self.__tempDir.createFilePath(".index.gz")
		self.__con.get(fileSetName + ".index.gz", path)
		nCountLines = 0
		with gzip.open(path, mode='rt', encoding='utf-8') as fin:
			for line in fin:
				nCountLines += 1
				line = line.strip('\n')
				(sSize, sTimeStamp, sRelPath) = line.split('\t')
				if (filePathFilter == None) or filePathFilter.canAccept(sRelPath):
					self.__fileSizes.append(int(sSize))
					if sRelPath.startswith("./"):
						sRelPath = sRelPath[2:]
					n = sRelPath.rfind('/')
					if n > 0:
						sRelDirPath = sRelPath[0:n]
						if (len(self.__dirPaths) == 0) or (self.__dirPaths[len(self.__dirPaths) - 1] != sRelDirPath):
							self.__dirPaths.append(sRelDirPath)
					self.__filePaths.append(sRelPath)
					timeStamp = datetime.utcfromtimestamp(float(sTimeStamp))
					self.__timeStamps.append(timeStamp)
		os.unlink(path)

		# remotely change into that data directory
		self.__con.chdir(rootDirPath + "/" + fileSetName)

		self.__rootDirPath = rootDirPath
		self.__fileSetName = fileSetName



	def countFiles(self):
		return len(self.__filePaths)



	def countDirs(self):
		return len(self.__dirPaths)



	def close(self):
		self.__con.close()
		self.__con = None



	#
	# Get an iterator that will provide access to the files.
	#
	# The iterator will return tuples containing the following fields:
	# * field 0: The index position.
	# * field 1: The maximum number of files this iterator will provide.
	# * field 2: The relative file path.
	# * field 3: The size of the file in bytes.
	# * field 4: A datetime object containing the last modification time stamp.
	# * field 5: Absolute path of the local file; use this to access the file contents.
	# * field 6: A boolean flag indicating if this file is temporary or the real file.
	#
	# An important note about the boolean flag on index 6:
	# <c>True</c> indicates: This is a temporary file provided in a temporary
	# directory ready for your processing. <c>False</c> indicates:
	# This is the real file and NOT to be deleted. If it is a temporary
	# file you are required to delete this file within your loop that
	# processes the iterator data. If you forget to do this downloaded files
	# may fill up your disk.
	#
	# @return	AbstractFilePathFilter filter		A file path filter object. (optional)
	# @return	iterator<tuple>		Returns an iterator that provides tuples as
	#								described above.
	#
	def getFileIterator(self, filter = None):
		if filter is None:
			selectedFilePaths = self.__filePaths
		else:
			selectedFilePaths = []
			for p in self.__filePaths:
				if filter.canAccept(p):
					selectedFilePaths.append(p)

		nmax = len(selectedFilePaths)
		i = 0
		for relFilePath in selectedFilePaths:
			localPath = self.__tempDir.createFilePath()
			remotePath = self.__rootDirPath + "/" + self.__fileSetName + "/" + relFilePath
			self.__con.get(remotePath, localPath)
			yield (i, nmax, relFilePath, self.__fileSizes[i], self.__timeStamps[i], localPath, True)
			i += 1



	#
	# Return a file tuple based on the path specified.
	#
	# The tuple returned contains the following fields:
	# * field 0: The relative file path.
	# * field 1: The size of the file in bytes.
	# * field 2: A datetime object containing the last modification time stamp.
	# * field 3: Absolute path of the local file; use this to access the file contents.
	# * field 4: A boolean flag indicating if this file is temporary or the real file.
	#
	# An important note about the boolean flag on index 4:
	# <c>True</c> indicates: This is a temporary file provided in a temporary
	# directory ready for your processing. <c>False</c> indicates:
	# This is the real file and NOT to be deleted. If it is a temporary
	# file you are required to delete this file within your loop that
	# processes the iterator data. If you forget to do this downloaded files
	# may fill up your disk.
	#
	# @param		string relFilePath		A file path.
	# @return		tuple					Returns a file tuple.
	#
	def getFileByPath(self, relFilePath):
		# TODO: optimize this!
		i = 0
		for relFilePath2 in self.__filePaths:
			if relFilePath2 == relFilePath:
				localPath = self.__tempDir.createFilePath()
				remotePath = self.__rootDirPath + "/" + self.__fileSetName + "/" + relFilePath
				self.__con.get(remotePath, localPath)
				return (relFilePath, self.__fileSizes[i], self.__timeStamps[i], localPath, True)
			i += 1
		return None



	#
	# Get an iterator that will provide file paths.
	#
	# The iterator will return tuples containing the following fields:
	# * field 0: The index position.
	# * field 1: The maximum number of files this iterator will provide.
	# * field 2: The relative file path.
	# * field 3: The size of the file in bytes.
	# * field 4: A datetime object containing the last modification time stamp.
	#
	# @return	iterator<tuple>		Returns an iterator that provides tuples as
	#								described above.
	#
	def getFilePathIterator(self):
		nmax = len(self.__filePaths)
		i = 0
		for relFilePath in self.__filePaths:
			yield (i, nmax, relFilePath, self.__fileSizes[i], self.__timeStamps[i])
			i += 1



	#
	# Get an iterator that will provide directory paths.
	#
	# The iterator will return tuples containing the following fields:
	# * field 0: The index position.
	# * field 1: The maximum number of files this iterator will provide.
	# * field 2: The relative directory path.
	#
	# @return	iterator<tuple>		Returns an iterator that provides tuples as
	#								described above.
	#
	def getDirPathIterator(self):
		nmax = len(self.__dirPaths)
		i = 0
		for relDirPath in self.__dirPaths:
			yield (i, nmax, relDirPath)
			i += 1



	#
	# Downloads the remote file and provides it as temporary file.
	#
	# @param		string remotePath		The file to download from the remote host.
	# @return		string		The path to the downloaded file.
	#
	#def download(self, remotePath):
	#	path = self.__tempDir.createFilePath()
	#	self.__con.get(remotePath, path)
	#	return path













