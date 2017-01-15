jk_fileaccess
=============

Introduction
------------

This python module provides a uniform interface to process files that are either stored locally or remotely.

**What this uniform interface is:** A simple way to iterate over a (very) large set of files. This should
be fast, this should be simple. That is the goal this module tries to achieve.

**What this uniform interface not is:** A full featured file system API. The classes are quite limited.
(Nevertheless feel free to aid in development of this module to extend the functionality of these classes.)

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/python-module-jk-fileaccess)
* [pypi.python.org](https://pypi.python.org/pypi?name=jk_temporary)

How to use this module
----------------------

### Requirements

This module will require the following python modules to operate:

* [jk_temporary](https://github.com/jkpubsrc/python-module-jk-temporary) - License: Apache 2.0
* [sh](https://pypi.python.org/pypi/sh) - License: MIT
* [pysftp](https://pypi.python.org/pypi/pysftp) - License: BSD

### Import

To import this module use the following statement:

```python
import jk_fileaccess
```

### Preparing data access

This module provides two kinds of classes:

* `SshRemoteFileInterface` to access data remotely using SSH and
* `LocalFileInterface` to access data locally.

Both classes are derived from `AbstractFileInterface` and overwrite abstract methods. Both classes are therefor
of the same structure and can be used interchangeably.

To access data you always have to provide a base directory. This will serve as the root for all file access.
But additionally you have to provide a file set name during construction. This name is basically the name
of a directory residing in the base directory. So the real file path on a system will be:

: `baseDirPath + '/' + fileSetName + '/' + relativeFilePath`

The data for `baseDirPath` and `fileSetName` need to be specified during construction of a file interface object
and do not change during the lifetime of that object.

To speed up accessing large amount of data remotely an index file is required. This file must reside in the
base directory and must be named similar as the file set:

: `baseDirPath + '/' + fileSetName + '.index.gz'`

The index is a text file containing information about each file line by line. Each line must contain of the
following three pieces of information separated by a single tab character:

1. The size of the file.
2. The last modification time stamp. This mus be provided in seconds since epoch (1970-01-01 00:00:00).
3. The relative file path, possibly with a leading `./`.

When such a file interface object is created it will read the file index first. This way it knows about what
files it can serve. This way tedious file operations can be avoided (which is quite handy if you need to
process millions of files, f.e. in scientific projects).

### Accessing remote data: Iterate over paths

Now you are able to instantiate the necessary classes in order to iterate over files, either locally or remotely via SSH:

```python
fs = jk_fileaccess.SshRemoteFileInterface(LOCAL_TEMP_DIR, SSH_HOST, SSH_PORT, SSH_USER, SSH_PWD, SSH_REMOTEPATH, FILESETNAME, None)

for v in fs.getDirPathIterator():
	print("\t" + str(v))

for v in fs.getFilePathIterator():
	print("\t" + str(v))
```

### Accessing remote data: Iterate over file data

In order to access the file data use some code like this:

```python
fs = jk_fileaccess.SshRemoteFileInterface(LOCAL_TEMP_DIR, SSH_HOST, SSH_PORT, SSH_USER, SSH_PWD, SSH_REMOTEPATH, FILESETNAME, None)

for (n, nmax, relFilePath, fileSize, fileDateTime, localFilePath, bIsLocalTempFile) in fs.getFileIterator():
	# now use the data
	...
```

If you perform remote access (like it is unavoidable with `SshRemoteFileInterface`) the last variable `bIsLocalTempFile` will always be `True`.

### Accessing local data

More for testing purposes than for real world scenarios you can access data locally as well using the same kind of API:

```python
fs = jk_fileaccess.LocalFileInterface(LOCALPATH, FILESETNAME, None)

for v in fs.getDirPathIterator():
	print("\t" + str(v))

for v in fs.getFilePathIterator():
	print("\t" + str(v))
```

Methods of file interface objects
---------------------------------

The next lines declare the methods a file interface object will provide for your convenience:

```python
#
# This method returns the number of files this object can provide.
#
# @return		int			Returns the number of files.
#
def countFiles(self)
```

```python
#
# This method returns the number of directories this object can provide.
#
# @return		int			Returns the number of directories.
#
def countDirs(self)
```

```python
#
# Close a data connection (if any exists). From now on calls to other methods of
# this object will fail.
#
def close(self)
```

```python
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
def getFileIterator(self, filter = None)
```

```python
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
def getDirPathIterator(self)
```

```python
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
def getFilePathIterator(self)
```

```python
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
def getFileByPath(self, relFilePath)
```

Contact Information
-------------------

This is Open Source code. That not only gives you the possibility of freely using this code it also
allows you to contribute. Feel free to contact the author(s) of this software listed below, either
for comments, collaboration requests, suggestions for improvement or reporting bugs:

* Jürgen Knauth: jknauth@uni-goettingen.de, pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



