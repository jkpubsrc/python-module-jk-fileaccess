


import re

from .LocalShare import LocalShare
from .SftpShare import SftpShare
from .CifsShare import CifsClient, CifsShare

import jk_pwdinput



class ShareFactory(object):



	__cifs_clients = {}

	__URLPATTERNS = [
		r"^(?P<stype>[a-z]+)://(?P<userName>[^[:/@]]+):(?P<password>[^[:/@]]+)@(?P<hostName>[a-z\.-_0-9]+):(?P<sPort>\d+)(?P<path>/.*)$",
		r"^(?P<stype>[a-z]+)://(?P<userName>[^[:/@]]+):(?P<password>[^[:/@]]+)@(?P<hostName>[a-z\.-_0-9]+)(?P<path>/.*)$",
		r"^(?P<stype>[a-z]+)://(?P<hostName>[a-z\.-_0-9]+):(?P<port>\d+)(?P<path>/.*)$",
		r"^(?P<stype>[a-z]+)://(?P<hostName>[a-z\.-_0-9]+)(?P<path>/.+)$",
		r"^(?P<stype>[a-z]+)://(?P<path>/.*)$"
	]



	@staticmethod
	def clearCache():
		ShareFactory.__cifs_clients.clear()

	#



	#
	# Call this method to create an object representing the share specified by the given URL. The following share types are supported:
	# * <c>file</c>
	# * <c>ssh</c>
	# * <c>cifs</c>
	#
	# Valid URLs would be:
	# * <c>file://localhost/home/jknauth/</c>
	# * <c>file://home/jknauth/</c>
	# * <c>smb://127.0.0.1/MyFancyShare/</c>
	# * <c>smb://exports.fs-services.myhost.com/MyFancyShare/</c>
	# * <c></c>
	# * <c></c>
	# * <c></c>
	#
	# Please note that for CIFS shares existing logins will be reused if possible.
	#
	@staticmethod
	def createShare(url = None, tempDirPath = None, shareType = None, login = None, password = None, hostname = None, port = None, path = None, shareName = None):
		if url != None:
			assert isinstance(url, str)

			data = None
			for pattern in ShareFactory.__URLPATTERNS:
				matchResult = re.match(pattern, url)
				if matchResult:
					data = {
						"stype": None,
						"userName": None,
						"password": None,
						"hostName": None,
						"port": None,
						"sPort": None,
						"path": None,
						"shareName": None
					}
					data.update(matchResult.groupdict())
					sPort = data.get("sPort", None)
					if sPort != None:
						data["port"] = int(sPort)
						del data["sPort"]
					break

			if data is None:
				raise Exception("Invalid URL specified: " + url)

		else:
			assert isinstance(shareType, str)
			assert isinstance(login, (str, type(None)))
			assert isinstance(password, (str, type(None)))
			assert isinstance(hostname, (str, type(None)))
			assert isinstance(port, (int, type(None)))
			assert isinstance(path, (str, type(None)))
			assert isinstance(shareName, (str, type(None)))

			data = {
				"stype": shareType,
				"userName": login,
				"password": password,
				"hostName": hostname,
				"port": port,
				"path": path,
				"shareName": shareName
			}

		# ----

		stype = data["stype"]

		if stype == "file":
			if (data["hostName"] is None) or (data["hostName"] == "localhost"):
				return LocalShare(data["path"])
			else:
				raise Exception("Invalid URL specified: " + url)

		if stype == "ssh":
			if data["hostName"] is None:
				raise Exception("No host name specified: " + url)
			if data["password"] is None:
				data["password"] = jk_pwdinput.readpwd("Password: ")
				if data["password"] is None:
					raise KeyboardInterrupt()
			return SftpShare(tempDirPath, data["hostName"], data["port"], data["userName"], data["password"], data["path"])

		if stype == "cifs":
			if data["hostName"] is None:
				raise Exception("No host name specified: " + url)
			matchResult = re.match("^/([a-z-_0-9]+)/^", data["path"])
			if matchResult:
				shareName = matchResult.group(1)
				data["path"] = "/"
			else:
				raise Exception("Invalid CIFS share URL")
			if data["password"] is None:
				data["password"] = jk_pwdinput.readpwd("Password: ")
				if data["password"] is None:
					raise KeyboardInterrupt()
			fingerPrint = data["hostName"] + ">><<" + data["userName"] + ">><<" + data["password"]
			c = ShareFactory.__cifs_clients.get(fingerPrint, None)
			if c is None:
				c = CifsClient(data["hostName"], data["userName"], data["password"])
				ShareFactory.__cifs_clients[fingerPrint] = c
			return c.openShare(shareName)

		else:
			raise Exception("Unknown share type: " + stype)

	#




#



