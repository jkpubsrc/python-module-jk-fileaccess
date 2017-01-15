#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import sh
import os
import time
import sys
import codecs
import random
import string

from .AbstractFilePathFilter import AbstractFilePathFilter



class PrefixFilePathFilter(AbstractFilePathFilter):

	def __init__(self, prefix):
		self.__prefix = prefix


	def canAccept(self, filePath):
		return filePath.startswith(self.__prefix)













