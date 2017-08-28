#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import datetime
import stat
import shutil

import jk_temporary

from .AbstractShare import *






#
# Instances of this object represent part of a local file system as a share.
#
class LocalShare(AbstractShare):

	#
	# @param		str baseDir		The base directory
	#
	def __init__(self, baseDir, fileMode = None, dirMode = None, uid = None, gid = None):
		assert isinstance(baseDir, str)
		assert len(baseDir) > 0
		assert baseDir[0] == "/"
		if fileMode != None:
			assert isinstance(fileMode, int)
		if dirMode != None:
			assert isinstance(dirMode, int)
		if (uid != None) or (gid != None):
			assert isinstance(uid, int)
			assert isinstance(gid, int)

		if len(baseDir) > 1:
			if baseDir.endswith("/"):
				baseDir = baseDir[:-1]

		self.__baseDir = baseDir
		self.__fileMode = fileMode
		self.__dirMode = dirMode
		self.__uid = gid
		self.__gid = uid

	#



	def setFileMode(self, fileMode):
		if fileMode != None:
			assert isinstance(fileMode, int)
		self.__fileMode = fileMode

	#



	def setDirectoryMode(self, dirMode):
		if dirMode != None:
			assert isinstance(dirMode, int)
		self.__dirMode = dirMode

	#



	def setUIDGID(self, uid, gid):
		if (uid != None) or (gid != None):
			assert isinstance(uid, int)
			assert isinstance(gid, int)
		self.__uid = gid
		self.__gid = uid

	#



	@property
	def isOpen(self):
		return True

	#



	@property
	def isClosed(self):
		return False

	#



	#
	# Get an URL representation of this share. This includes the type, a server and a path.
	# This method will not return more specific information as f.e. authentification data.
	#
	# @return	str			Returns a string such as "type://hostname:port/path/to/base/dir/"
	#
	@property
	def urlBase(self):
		ret = "file://localhost" + self.__baseDir
		if ret[-1] != "/":
			ret += "/"
		return ret

	#



	@property
	def hostName(self):
		return "localhost"

	#



	@property
	def shareName(self):
		return self.urlBase

	#



	#
	# TODO: normalize specified path
	#
	def __buildPath(self, path):
		if path.startswith("/"):
			if self.__baseDir == "/":
				return path
			else:
				return self.__baseDir + path
		else:
			raise Exception("Not an absolute path: " + path)

	#



	def __unbuildPath(self, path):
		if self.__baseDir == "/":
			return path
		else:
			return path[len(self.__baseDir):]

	#



	#
	# Upload the locally existing file to the specified file on the share.
	#
	# @param		str localInputFilePath				The path of the local file to upload
	# @param		str remoteOutputFilePath			The path of the file on the share that will receive the data
	# @param		bool bRemoveLocalFileAfterUpload	Specify <c>True</c> here if the local file is no longer needed after upload.
	#													If supported the implementation might be able to perform some kind of move
	#													operation instead of a copy with a successing delete.
	#
	def uploadLocalFile(self, localInputFilePath, remoteOutputFilePath, bRemoveLocalFileAfterUpload = False):
		path = self.__buildPath(remoteOutputFilePath)

		# fileSize = os.stat(localInputFilePath).st_size

		if bRemoveLocalFileAfterUpload:
			try:
				os.rename(localInputFilePath, path)
				return
			except Exception as e:
				pass

		with open(localInputFilePath, mode="rb") as fin:
			with open(path, mode="wb") as fout:
				if self.__fileMode != None:
					os.fchmod(fout, self.__fileMode)
				if self.__uid != None:
					os.fchown(fout, self.__uid, self.__gid)
				shutil.copyfileobj(fin, fout, 65536)

		# fileSize2 = os.stat(path).st_size
		# assert fileSize == fileSize2

		if bRemoveLocalFileAfterUpload:
			os.unlink(localInputFilePath)

	#



	def writeAllDataToFile(self, remoteOutputFilePath, fileData):
		remotePath = self.__buildPath(remoteOutputFilePath)
		# print(">> " + remotePath)
		# print("\t" + str(len(fileData)))
		with open(remotePath, mode="wb") as fout:
			if self.__fileMode != None:
				os.fchmod(fout, self.__fileMode)
			if self.__uid != None:
				os.fchown(fout, self.__uid, self.__gid)
			fout.write(fileData)

	#



	def readAllDataFromFile(self, path):
		path = self.__buildPath(path)
		# print("<< " + path)
		with open(path, mode="rb") as fin:
			myData = fin.read()
		# print("\t" + str(len(myData)))
		return myData

	#



	def deleteEmptyDirectory(self, path):
		path = self.__buildPath(path)
		os.rmdir(path)

	#



	def deleteFile(self, path):
		path = self.__buildPath(path)
		os.unlink(path)

	#



	def createDirectory(self, path):
		path = self.__buildPath(path)
		os.mkdir(path)
		if self.__dirMode != None:
			os.chmod(path, self.__dirMode)
		if self.__uid != None:
			os.chown(path, self.__uid, self.__gid)

	#



	#
	# Returns the contents of the specified directory. Only the file names are returned. This method is significantly faster
	# than <c>listDirectoryContent()</c> as no additional data needs to be retrieved for each directory entry.
	#
	# @return		string[]		Returns an array of strings containing the names of the directory entries.
	#
	#
	def listDirectoryContentNames(self, path, bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = True):
		path = self.__buildPath(path)
		if path.endswith("/"):
			path2 = path
			if len(path) > 1:
				path = path[:-1]
		else:
			path2 = path + "/"
		ret = []
		for dirEntry in os.listdir(path):
			statStruct = os.stat(path2 + dirEntry)
			if stat.S_ISDIR(statStruct.st_mode):
				if bIncludeSubDirs:
					ret.append(dirEntry)
			elif stat.S_ISREG(statStruct.st_mode):
				if bIncludeFiles:
					ret.append(dirEntry)
			elif bIncludeOthers:
				ret.append(dirEntry)
		return ret

	#



	#
	# Returns the contents of the specified directory.
	#
	# @return		tuple[]		Returns an array of tuples containing data about the directory entries. Each tuple contains the following data:
	#							* string: The file or directory Name
	#							* string: A single character named 'f' or 'd' indicating file or directory
	#							* int: The file or directory mode (= access flags)
	#							* int: The user ID
	#							* int: The group ID
	#							* int: The size if the file or <c>None</c> if a directory
	#							* int: The modification time stamp in milliseconds (!) since Epoch or <c>None</c> if a directory
	#
	def listDirectoryContent(self, path, bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = True):
		path = self.__buildPath(path)
		if path.endswith("/"):
			path2 = path
			if len(path) > 1:
				path = path[:-1]
		else:
			path2 = path + "/"
		ret = []
		for dirEntry in os.listdir(path):
			statStruct = os.stat(path2 + dirEntry)
			if stat.S_ISDIR(statStruct.st_mode):
				if bIncludeSubDirs:
					ret.append((dirEntry, 'd', statStruct.st_mode, statStruct.st_uid, statStruct.st_gid, None, None))
			elif stat.S_ISREG(statStruct.st_mode):
				if bIncludeFiles:
					ret.append((dirEntry, 'f', statStruct.st_mode, statStruct.st_uid, statStruct.st_gid, statStruct.st_size, statStruct.st_mtime * 1000))
			elif bIncludeOthers:
				ret.append((dirEntry, '?', statStruct.st_mode, statStruct.st_uid, statStruct.st_gid, statStruct.st_size, statStruct.st_mtime * 1000))
		return ret

	#



	def _createRandomFilePath(self, dirPath, prefix = 'tmp_', randomNameLength = 32, postfix = ''):
		dirPath2 = self.__buildPath(dirPath)
		dirPath = jk_temporary.createRandomFilePath(dirPath2, prefix = prefix, randomNameLength = randomNameLength, postfix = postfix)
		return self.__unbuildPath(dirPath)

	#



#






