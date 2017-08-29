#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import datetime






__EPOCH = datetime.datetime.utcfromtimestamp(0)

def x__nowInMillisecondsSinceEpoch():
	return int((datetime.datetime.utcnow() - __EPOCH).total_seconds() * 1000)




class AbstractShare(object):

	@property
	def hostName(self):
		pass

	@property
	def shareName(self):
		pass

	@property
	def isOpen(self):
		pass

	@property
	def isClosed(self):
		pass

	#
	# Get an URL representation of this share. This includes the type, a server and a path.
	# This method will not return more specific information as f.e. authentification data.
	#
	# @return	str			Returns a string such as "type://hostname:port/path/to/base/dir/"
	#
	@property
	def urlBase(self):
		pass

	#
	# Set the mode of the files. If new files are created, they are created with the access right specified here.
	# Please note that not all shares might support this feature.
	#
	def setFileMode(self, fileMode):
		pass
	#

	#
	# Set the mode of the directories. If new directories are created, they are created with the access right specified here.
	# Please note that not all shares might support this feature.
	#
	def setDirectoryMode(self, dirMode):
		pass
	#

	#
	# Set the UID and GID of the files and directories. If new files or directories are created, they are created with the user and group ID specified here.
	# Please note that not all shares might support this feature.
	#
	def setUIDGID(self, uid, gid):
		pass
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
		pass

	#
	# Write text or binary data file.
	#
	# Note: Text is written UTF-8 encoded. If you require different encoding, convert the text to binary yourself before invoking
	# this method.
	#
	def writeAllDataToFile(self, remoteOutputFilePath, fileData):
		if isinstance(fileData, str):
			fileData = fileData.encode("utf-8")
		elif isinstance(fileData, (bytearray, bytes)):
			pass
		else:
			raise Exception("Data must be provided as string or byte object!")

		self._writeAllDataToFile(remoteOutputFilePath, fileData)
	#



	def _writeAllDataToFile(self, remoteOutputFilePath, fileData):
		pass

	def readAllDataFromFile(self, remoteInputFilePath):
		pass

	def deleteEmptyDirectory(self, path):
		pass

	def deleteFile(self, path):
		pass

	def createDirectory(self, path):
		pass

	#
	# Verifies the specified path. Processing the path by this method will recognize "." and ".." elements.
	#
	# @param		str path						The path to process.
	# @param		bool bRaiseExceptionOnError		Specify <c>True</c> here to raise an exception on error.
	#												Specify <c>False</c> to simply have returned <c>None</c>.
	# @return		bool							Either returns <c>False</c> on error or <c>True</c> on success.
	#
	def _verifyAbsolutePath(self, path, bRaiseExceptionOnError = True):
		if not isinstance(path, str):
			if bRaiseExceptionOnError:
				raise Exception("String expected, but '" + str(type(path)) + "' was specified!")
			else:
				return False
		if path[0] != "/":
			if bRaiseExceptionOnError:
				raise Exception("Path is not an absolute path!")
			else:
				return False
		if path == "/":
			return True

		pathElements = path[1:].split("/")
		for pathElement in pathElements:
			if (pathElement == "..") or (pathElement == "."):
				if bRaiseExceptionOnError:
					raise Exception("Not a valid path!")
				else:
					return False

		return True
	#

	#
	# Normalizes and verifies the specified path. Processing the path by this method will remove "." and ".." elements.
	#
	# @param		str path						The path to process.
	# @param		bool bRaiseExceptionOnError		Specify <c>True</c> here to raise an exception on error.
	#												Specify <c>False</c> to simply have returned <c>None</c>.
	# @return		str								Either returns <c>None</c> on error or a normalized path on success.
	#
	def _normalizeAndVerifyAbsolutePath(self, path, bRaiseExceptionOnError = True):
		if not isinstance(path, str):
			if bRaiseExceptionOnError:
				raise Exception("String expected, but '" + str(type(path)) + "' was specified!")
			else:
				return None
		if path[0] != "/":
			if bRaiseExceptionOnError:
				raise Exception("Path is not an absolute path!")
			else:
				return None
		if path == "/":
			return "/"

		pathElements = path[1:].split("/")

		temp = []
		for pathElement in pathElements:
			if pathElement == ".":
				continue
			elif pathElement == "..":
				if len(temp) > 0:
					temp = temp[:-1]
				else:
					if bRaiseExceptionOnError:
						raise Exception("Path is not a valid absolute path!")
					else:
						return None
				continue
			else:
				temp.append(pathElement)

		ret = ""
		for pathElement in temp:
			ret += "/" + pathElement
		return ret
	#

	#
	# Normalize the specified (absolute) path. Processing the path by this method will remove "." and ".." elements.
	#
	# @param		str path						The path to process.
	# @return		str								Returns the normalized path on success.
	#
	def normalizePath(self, path):
		return self._normalizeAndVerifyAbsolutePath(path)
	#

	#
	# Ensure that the specified directory exists.
	#
	# @param		str path		The directory path to create.
	# @return		bool			Returns <c>True</c> if at least one directory needed to be created. <c>False</c> is returned
	#								if all directories already existed.
	#
	def ensureDirectoryExists(self, path):
		path = self._normalizeAndVerifyAbsolutePath(path)
		if path == "/":
			return False

		pathElements = path[1:].split("/")

		bDirectoryCreated = False

		p = "/"
		for pathElement in pathElements:
			dirNames = self.listDirectoryContentNames(p, bIncludeSubDirs = True, bIncludeFiles = False, bIncludeOthers = False)
			if pathElement not in dirNames:
				# directory not found => create it
				self.createDirectory(p + "/" + pathElement)
				bDirectoryCreated = True
			if len(p) > 1:
				p += "/"
			p += pathElement

		return bDirectoryCreated
	#

	#
	# Get a list of all directories existing below the specified path.
	#
	# @param		str path		The (existing) start path for listing directories.
	# @return		str[]			Returns a list of absolut paths.
	#
	def listAllDirectoriesRecursively(self, path = "/"):
		ret = []
		for dirName in self.listDirectoryContentNames(path, bIncludeSubDirs = True, bIncludeFiles = False, bIncludeOthers = False):
			fullP = os.path.join(path, dirName)
			ret.append(fullP)
			ret.extend(self.listAllDirectoriesRecursively(fullP))
		return ret

	#
	# Returns the contents of the specified directory in form of a list of strings.
	#
	# @param		str path				The (existing) absolute path where to look for directory content.
	# @param		bool bIncludeSubDirs	Specify <c>True</c> here to include subdirectories.
	# @param		bool bIncludeFiles		Specify <c>True</c> here to include files.
	# @param		bool bIncludeOthers		Specify <c>True</c> here to include any other kind of file like entry.
	# @return		string[]	Returns an array of directory entry names.
	#
	def listDirectoryContentNames(self, path, bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = True):
		pass

	#
	# Returns the contents of the specified directory.
	#
	# @param		str path				The (existing) absolute path where to look for directory content.
	# @param		bool bIncludeSubDirs	Specify <c>True</c> here to include subdirectories.
	# @param		bool bIncludeFiles		Specify <c>True</c> here to include files.
	# @param		bool bIncludeOthers		Specify <c>True</c> here to include any other kind of file like entry.
	# @return		tuple[]			Returns an array of tuples containing data about the directory entries. Each tuple contains the following data:
	#								* string: The file or directory name
	#								* string: A single character named 'f' or 'd' indicating file or directory
	#								* int: The file or directory mode (= access flags)
	#								* int: The user ID
	#								* int: The group ID
	#								* int: The size if the file or <c>None</c> if a directory
	#								* int: The modification time stamp in milliseconds (!) since Epoch or <c>None</c> if a directory
	#
	def listDirectoryContent(self, path, bIncludeSubDirs = True, bIncludeFiles = True, bIncludeOthers = True):
		pass

	def _createRandomFilePath(self, dirPath, prefix = 'tmp_', randomNameLength = 32, postfix = ''):
		pass

	#
	# Perform a speed test by writing, reading and deleting files to a temporarily created directory.
	#
	# @param	int numFiles		The number of files to create
	# @param	int fileSize		The size of each file to create
	# @return	dict				Returns a dictionary containing the following key-value-pairs:
	#								* 'urlBase' - The URL base of this share
	#								* 'hostName' - The host name of this share
	#								* 'shareName' - The name of this share
	#								* 'avgWrite' - The average write speed of a single file (in milliseconds)
	#								* 'avgRead' - The average read speed of a single file (in milliseconds)
	#								* 'avgDel' - The average speed it took to delete a single file (in milliseconds)
	#
	def performSpeedTest(self, baseDirPath = "/", numFiles = 2000, fileSize = 65536):
		tmpDirPath = self._createRandomFilePath(baseDirPath, randomNameLength = 64)
		print("Creating directory: " + tmpDirPath)
		self.createDirectory(tmpDirPath)

		data = bytes(fileSize)
		tmpFilePaths = []
		print("Creating " + str(numFiles) + " files with " + str(int(fileSize / 1024)) + "k data:")
		t1 = x__nowInMillisecondsSinceEpoch()
		for i in range(0, numFiles):
			print("\r\t" + str(i + 1), end='')
			tmpFilePath = self._createRandomFilePath(tmpDirPath +  "/", randomNameLength = 32, postfix = '.something')
			tmpFilePaths.append(tmpFilePath)
			self.writeAllDataToFile(tmpFilePath, data)
		tCreateTotal = x__nowInMillisecondsSinceEpoch() - t1
		tCreateAvg = tCreateTotal / numFiles
		print("\r\t" + str(tCreateTotal) + " ms in total, " + str(tCreateAvg) + " ms per file")

		print("Reading the " + str(numFiles) + " files ...")
		t1 = x__nowInMillisecondsSinceEpoch()
		for i in range(0, numFiles):
			print("\r\t" + str(i + 1), end='')
			tmpFilePath = tmpFilePaths[i]
			myData = self.readAllDataFromFile(tmpFilePath)
		tReadTotal = x__nowInMillisecondsSinceEpoch() - t1
		tReadAvg = tReadTotal / numFiles
		print("\r\t" + str(tReadTotal) + " ms in total, " + str(tReadAvg) + " ms per file")

		print("Deleting the " + str(numFiles) + " files ...")
		t1 = x__nowInMillisecondsSinceEpoch()
		for i in range(0, numFiles):
			print("\r\t" + str(i + 1), end='')
			tmpFilePath = tmpFilePaths[i]
			self.deleteFile(tmpFilePath)
		tDelTotal = x__nowInMillisecondsSinceEpoch() - t1
		tDelAvg = tDelTotal / numFiles
		print("\r\t" + str(tDelTotal) + " ms in total, " + str(tDelAvg) + " ms per file")

		print("Deleting directory: " + tmpDirPath)
		self.deleteEmptyDirectory(tmpDirPath)

		return {
			"urlBase": self.urlBase,
			"hostName": self.hostName,
			"shareName": self.shareName,
			"avgWrite": tCreateAvg,
			"avgRead": tReadAvg,
			"avgDel": tDelAvg
		}

	#

#






