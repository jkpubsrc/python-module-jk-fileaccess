#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import os
import time
import sys
import codecs
import random
import string




class AbstractFileInterface(object):

	#
	# This method returns the number of files this object can provide.
	#
	# @return		int			Returns the number of files.
	#
	def countFiles(self):
		raise Exception("Subclasses must overwrite this method: countFiles()")

	#
	# This method returns the number of directories this object can provide.
	#
	# @return		int			Returns the number of directories.
	#
	def countDirs(self):
		raise Exception("Subclasses must overwrite this method: countDirs()")

	#
	# Close a data connection (if any exists). From now on calls to other methods of
	# this object will fail.
	#
	def close(self):
		raise Exception("Subclasses must overwrite this method: close()")

	#
	# Get an iterator that will provide access to the files.
	# If the file is located on a remote system it will be
	# copied to a local directory within this method so that
	# it's data will immediately be ready for use.
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
		raise Exception("Subclasses must overwrite this method: getFileIterator()")

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
		raise Exception("Subclasses must overwrite this method: getDirPathIterator()")

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
		raise Exception("Subclasses must overwrite this method: getFilePathIterator()")

	#
	# Return a file tuple based on the path specified.
	# If the file is located on a remote system it will be
	# copied to a local directory within this method so that
	# it's data will immediately be ready for use.
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
		raise Exception("Subclasses must overwrite this method: getFileByPath()")









