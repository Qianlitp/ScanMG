#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo import *

client = MongoClient('115.29.32.26', 27017)
print client.database_names()
