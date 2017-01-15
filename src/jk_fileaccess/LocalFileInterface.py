#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import codecs
import random
import string
import gzip
from datetime import datetime

import sh

from .AbstractFileInterface import AbstractFileInterface




class LocalFileInterface(AbstractFileInterface):

	def __init__(self, rootDirPath, fileSetName, filePathFilter):
		rootDirPath = os.path.abspath(rootDirPath)

		self.__rootDirPath = rootDirPath
		self.__fileSetName = fileSetName
		self.__fileSizes = []
		self.__filePaths = []
		self.__dirPaths = []
		self.__timeStamps = []

		# download file index
		path = os.path.join(rootDirPath, fileSetName + ".index.gz")
		nCountLines = 0
		with gzip.open(path, mode='rt', encoding='utf-8') as fin:
			for line in fin:
				nCountLines += 1
				line = line.strip('\n')
				(sSize, sTimeStamp, sRelPath) = line.split('\t')
				if (filePathFilter is None) or filePathFilter.canAccept(sRelPath):
					self.__fileSizes.append(int(sSize))
					if sRelPath.startswith("./"):
						sRelPath = sRelPath[2:]
					n = sRelPath.rfind('/')
					if n > 0:
						sRelDirPath = sRelPath[0:n]
						if (len(self.__dirPaths) == 0) or (self.__dirPaths[len(self.__dirPaths) - 1] != sRelDirPath):
							self.__dirPaths.append(sRelDirPath)
					abspath = os.path.abspath(os.path.join(rootDirPath, sRelPath))
					abspath = abspath[len(rootDirPath) + 1:]
					self.__filePaths.append(abspath)
					timeStamp = datetime.utcfromtimestamp(float(sTimeStamp))
					self.__timeStamps.append(timeStamp)



	def countFiles(self):
		return len(self.__filePaths)



	def countDirs(self):
		return len(self.__dirPaths)



	def close(self):
		pass



	#
	# Get an iterator that will provide access to the files.
	#
	# The iterator will return tuples containin the following fields:
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
	# @return	iterator<tuple>						Returns an iterator that provides tuples as
	#												described above.
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
			path = os.path.join(self.__rootDirPath, self.__fileSetName, relFilePath)
			yield (i, nmax, relFilePath, self.__fileSizes[i], self.__timeStamps[i], path, False)
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
		i = 0
		for relFilePath2 in self.__filePaths:
			if relFilePath == relFilePath2:
				path = os.path.join(self.__rootDirPath, self.__fileSetName, relFilePath)
				yield (relFilePath, self.__fileSizes[i], self.__timeStamps[i], path, False)
			i += 1
		return None



	#
	# Get an iterator that will provide file paths.
	#
	# The iterator will return tuples containin the following fields:
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
	# The iterator will return tuples containin the following fields:
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















