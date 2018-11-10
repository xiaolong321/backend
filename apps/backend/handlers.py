#!/usr/bin/python
# -*- coding: utf-8 -*-

# app
import os
import re

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))

hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_handler\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    __import__(model_name, globals(), locals(), [model_name], 1)
