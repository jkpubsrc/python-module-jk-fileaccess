#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import sh
import os
import time
import sys
import codecs
import random
import string




class AbstractFilePathFilter(object):

	def canAccept(self, filePath):
		raise Exception("Subclasses must implement this method: canAccept()")













