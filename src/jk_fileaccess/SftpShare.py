#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import datetime
import pysftp
import stat

import jk_temporary

from .AbstractShare import *






#
# This class gives access to a directory tree on a remote host via an SSH connection.
#
class SftpShare(AbstractShare):

	#
	# @param		str tempDirPath			(optional) A temporary directory that serves as a container for file transfers.
	#										If such a directory is provided for unknown reasons the data transfer speed is much better.
	#										If you want to make use of that feature, provide an existing directory here.
	#										For security reasons consider to set the mode for this directory to 0o600.
	# @param		str hostName			The host to connect to
	# @param		int port				The network port to connect to
	# @param		str baseDir				The base directory on the remote file system
	#
	def __init__(self, tempDirPath, hostName, port, userName, password, baseDir):
		if tempDirPath != None:
			assert isinstance(tempDirPath, str)
			assert baseDir[0] == "/"
			if len(tempDirPath) > 1:
				if tempDirPath.endswith("/"):
					tempDirPath = tempDirPath[:-1]
		assert isinstance(hostName, str)
		assert len(hostName) > 0
		assert isinstance(port, int)
		assert (port > 0) and (port <= 65535)
		assert isinstance(userName, str)
		assert len(userName) > 0
		assert isinstance(password, str)
		assert len(password) > 0
		assert isinstance(baseDir, str)
		assert len(baseDir) > 0
		assert baseDir[0] == "/"
		if len(baseDir) > 1:
			if baseDir.endswith("/"):
				baseDir = baseDir[:-1]
		self.__baseDir = baseDir
		self.__tempDirPath = tempDirPath
		self.__hostName = hostName
		self.__port = port
		self.__userName = userName
		self.__password = password

		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None
		self.__con = pysftp.Connection(hostName, port=port, username=userName, password=password, cnopts=cnopts)
		self.__con.chdir(baseDir)

	#



	@property
	def isOpen(self):
		return self.__con != None

	#



	@property
	def isClosed(self):
		return self.__con is None

	#



	#
	# Get an URL representation of this share. This includes the type, a server and a path.
	# This method will not return more specific information as f.e. authentification data.
	#
	# @return	str			Returns a string such as "type://hostname:port/path/to/base/dir/"
	#
	@property
	def urlBase(self):
		ret = "ssh://" + self.__hostName + ":" + str(self.__port) + self.__baseDir
		if ret[-1] != "/":
			ret += "/"
		return ret

	#



	@property
	def hostName(self):
		return self.__hostName

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
		remotePath = self.__buildPath(remoteOutputFilePath)
		remoteDir = os.path.dirname(remotePath)

		self.__con.chdir(remoteDir)
		self.__con.put(localInputFilePath)

		if bRemoveLocalFileAfterUpload:
			os.unlink(localInputFilePath)

	#



	def writeAllDataToFile(self, remoteOutputFilePath, fileData):
		remotePath = self.__buildPath(remoteOutputFilePath)
		if self.__tempDirPath is None:
			fd = self.__con.open(remotePath, mode='w', bufsize=65536)
			fd.write(fileData)
			fd.close()
		else:
			remoteDir = os.path.dirname(remotePath)
			remoteFileName = os.path.basename(remotePath)
			localTmpPath = os.path.join(self.__tempDirPath, remoteFileName)
			fd = open(localTmpPath, 'wb', 0o600)
			fd.write(fileData)
			fd.close()
			self.__con.chdir(remoteDir)
			self.__con.put(localTmpPath)
			os.unlink(localTmpPath)

	#



	def readAllDataFromFile(self, remoteInputFilePath):
		remotePath = self.__buildPath(remoteInputFilePath)
		if self.__tempDirPath is None:
			fd = self.__con.open(remotePath, mode='r', bufsize=65536)
			fileData = fd.read()
			fd.close()
		else:
			remoteDir = os.path.dirname(remotePath)
			remoteFileName = os.path.basename(remotePath)
			localTmpPath = os.path.join(self.__tempDirPath, remoteFileName)
			self.__con.get(remotePath, localpath=localTmpPath)
			fd = open(localTmpPath, 'rb')
			fileData = fd.read()
			fd.close()
			os.unlink(localTmpPath)
			return fileData

	#



	def deleteEmptyDirectory(self, path):
		remotePath = self.__buildPath(path)
		self.__con.rmdir(remotePath)

	#



	def deleteFile(self, path):
		remotePath = self.__buildPath(path)
		self.__con.remove(remotePath)

	#



	def createDirectory(self, path):
		remotePath = self.__buildPath(path)
		self.__con.mkdir(remotePath)

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
		for dirEntry in self.__con.listdir_attr(path):
			if stat.S_ISDIR(dirEntry.st_mode):
				if bIncludeSubDirs:
					ret.append(dirEntry.filename)
			elif stat.S_ISREG(dirEntry.st_mode):
				if bIncludeFiles:
					ret.append(dirEntry.filename)
			elif bIncludeOthers:
				ret.append(dirEntry.filename)
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
		for dirEntry in self.__con.listdir_attr(path):
			if stat.S_ISDIR(dirEntry.st_mode):
				if bIncludeSubDirs:
					ret.append((dirEntry.filename, 'd', dirEntry.st_mode, dirEntry.st_uid, dirEntry.st_gid, None, None))
			elif stat.S_ISREG(dirEntry.st_mode):
				if bIncludeFiles:
					ret.append((dirEntry.filename, 'f', dirEntry.st_mode, dirEntry.st_uid, dirEntry.st_gid, dirEntry.st_size, dirEntry.st_mtime * 1000))
			elif bIncludeOthers:
				ret.append((dirEntry.filename, '?', dirEntry.st_mode, dirEntry.st_uid, dirEntry.st_gid, dirEntry.st_size, dirEntry.st_mtime * 1000))
		return ret

	#



	def _createRandomFilePath(self, dirPath, prefix = 'tmp_', randomNameLength = 32, postfix = ''):
		dirPath2 = self.__buildPath(dirPath)
		dirPath = jk_temporary.createRandomFilePath(dirPath2, prefix = prefix, randomNameLength = randomNameLength, postfix = postfix)
		return self.__unbuildPath(dirPath)

	#

#






