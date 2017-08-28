#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import datetime
import shutil
import stat
import smbc

import jk_temporary

from .AbstractShare import *






class CifsShare(AbstractShare):

	#
	# @param		int smbcType		This seems to be
	#									- 3 for regular shares,
	#									- 6 for special shares,
	#									- 7 for directories,
	#									- 8 for files
	# @param		str comment			The comment describing this share
	#
	def __init__(self, parent, ctx, shareName, smbcType, comment):
		self.__parent = parent
		self.__ctx = ctx
		self.__shareName = shareName
		if smbcType == 3:
			self.__isSpecial = False
		elif smbcType == 6:
			self.__isSpecial = True
		else:
			raise Exception("Invalid type specified!")
		self.__comment = comment
		self.__urlBase = "smb://" + self.__parent.hostName + "/" + shareName + "/"

	#



	@property
	def hostName(self):
		return self.__parent.hostName

	#



	#
	# Get an URL representation of this share. This includes the type, a server and a path.
	# This method will not return more specific information as f.e. authentification data.
	#
	# @return	str			Returns a string such as "type://hostname:port/path/to/base/dir/"
	#
	@property
	def urlBase(self):
		return self.__urlBase

	#



	@property
	def comment(self):
		return self.__comment

	#



	@property
	def isSpecial(self):
		return self.__isSpecial

	#



	@property
	def shareName(self):
		return self.__shareName

	#



	@property
	def isOpen(self):
		return self.__ctx is not None

	#



	@property
	def isClosed(self):
		return self.__ctx is None

	#



	def __close(self):
		self.__ctx = None

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
		if remoteOutputFilePath.startswith("/"):
			remotePath = self.__urlBase + remoteOutputFilePath[1:]
		else:
			raise Exception("Not an absolute path: " + remoteOutputFilePath)
		# TODO: normalize specified path

		fileSize = os.stat(localInputFilePath).st_size

		with open(localInputFilePath, momde="rb") as fin:
			with self.__ctx.open(remotePath, os.O_CREAT | os.O_WRONLY) as fout:
				shutil.copyfileobj(fin, fout, 65536)

		if bRemoveLocalFileAfterUpload:
			os.unlink(localInputFilePath)

	#



	def writeAllDataToFile(self, remoteOutputFilePath, fileData):
		if remoteOutputFilePath.startswith("/"):
			remotePath = self.__urlBase + remoteOutputFilePath[1:]
		else:
			raise Exception("Not an absolute path: " + remoteOutputFilePath)
		# TODO: normalize specified path
		f = self.__ctx.open(remotePath, os.O_CREAT | os.O_WRONLY)
		f.write(fileData)
		f.close()

	#



	def readAllDataFromFile(self, path):
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		# TODO: normalize specified path
		f = self.__ctx.open(path2, os.O_RDONLY)
		myData = f.read()
		f.close()
		return myData

	#



	def deleteEmptyDirectory(self, path):
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		# TODO: normalize specified path
		self.__ctx.rmdir(path2)

	#



	def deleteFile(self, path):
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		# TODO: normalize specified path
		self.__ctx.unlink(path2)

	#



	def createDirectory(self, path):
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		# TODO: normalize specified path
		self.__ctx.mkdir(path2)

	#



	#
	# Returns the contents of the specified directory. Only the file names are returned.
	#
	# @return		string[]		Returns an array of strings containing the names of the directory entries.
	#
	#
	def listDirectoryContentNames(self, path, bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = True):
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		if path2.endswith("/"):
			path2 = path2[:-1]
		ret = []
		d = self.__ctx.opendir(path2)
		entries = d.getdents()
		for entry in entries:
			if (entry.name == ".") or  (entry.name == ".."):
				continue
			if bIncludeSubDirs and bIncludeFiles:
				ret.append(entry.name)
			else:
				(st_mode, st_inode, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime) = self.__ctx.stat(path + "/" + entry.name)
				if stat.S_ISDIR(st_mode): #entry.smbc_type == 7:
					if bIncludeSubDirs:
						ret.append(entry.name)
				elif stat.S_ISREG(st_mode): #entry.smbc_type == 8:
					if bIncludeFiles:
						ret.append(entry.name)
				else:
					raise Exception("Unexpected type ID found for entry '" + entry.name + "': " + str(entry.smbc_type))

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
		if path.startswith("/"):
			path2 = self.__urlBase + path[1:]
		else:
			raise Exception("Not an absolute path: " + path)
		if path2.endswith("/"):
			path2 = path2[:-1]
		ret = []
		d = self.__ctx.opendir(path2)
		entries = d.getdents()
		for entry in entries:
			if (entry.name == ".") or  (entry.name == ".."):
				continue
			(st_mode, st_inode, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime) = self.__ctx.stat(path + "/" + entry.name)
			if stat.S_ISDIR(st_mode): #entry.smbc_type == 7:
				if bIncludeSubDirs:
					ret.append((entry.name, 'd', st_mode, st_uid, st_gid, None, None))
			elif stat.S_ISREG(st_mode): #entry.smbc_type == 8:
				if bIncludeFiles:
					ret.append((entry.name, 'f', st_mode, st_uid, st_gid, st_size, st_mtime * 1000))
			else:
				raise Exception("Unexpected type ID found for entry '" + entry.name + "': " + str(entry.smbc_type))
		return ret

	#



	def _createRandomFilePath(self, dirPath, prefix = 'tmp_', randomNameLength = 32, postfix = ''):
		return jk_temporary.createRandomFilePath(dirPath, randomNameLength = 64, postfix = '')

	#

#






class CifsClient(object):

	def __init__(self, serverIPAddress, userName, password):
		self.__serverIPAddress = serverIPAddress
		self.__userName = userName
		self.__password = password

		self.__ctx = smbc.Context()
		self.__ctx.optionNoAutoAnonymousLogin = True
		cb = lambda se, sh, w, u, p: (w, self.__userName, self.__password)
		self.__ctx.functionAuthData = cb

		self.__openShares = {}
		self.__urlBase = "smb://" + serverIPAddress + "/"

	#



	#
	# Get an URL representation of this share. This includes the type, a server and a path.
	# This method will not return more specific information as f.e. authentification data.
	#
	# @return	str			Returns a string such as "type://hostname:port/path/to/base/dir/"
	#
	def urlBase(self):
		return self.__urlBase

	#



	@property
	def hostName(self):
		return self.__serverIPAddress

	#



	@property
	def userName(self):
		return self.__userName

	#



	@property
	def isOpen(self):
		return self.__ctx is not None

	#



	@property
	def isClosed(self):
		return self.__ctx is None

	#



	#
	# Get a list of Samba Shares
	#
	def listShareNames(self):
		ret = []
		dir = self.__ctx.opendir("smb://" + self.__serverIPAddress + "/")
		entries = dir.getdents()
		for entry in entries:
			ret.append(entry.name)
		return ret

	#



	def __getShareObject(self, shareName):
		dir = self.__ctx.opendir("smb://" + self.__serverIPAddress + "/")
		entries = dir.getdents()
		for entry in entriesopenShare:
			if shareName == entry.name:
				return entry
		return None
		#raise Exception("No such share: " + shareName)

	#



	#
	# Return an an object representing a share.
	#
	def openShare(self, shareName):
		if self.__ctx is None:
			raise Exception("Connection already closed.")
		if shareName in self.__openShares:
			return self.__openShares[shareName]
		shareObj = self.__getShareObject(shareName)
		if shareObj is None:
			raise Exception("No such share: " + shareName)
		else:
			cs = CifsShare(self, self.__ctx, shareName, shareObj.smbc_type, shareObj.comment)
			self.__openShares[shareName] = cs
			return cs
	#



	def close(self):
		self.__ctx = None
		for cifsShare in self.__openShares.values():
			cifsShare.__close()
		self.__openShares = {}

	#

#






