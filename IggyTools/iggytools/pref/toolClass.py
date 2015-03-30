import os.path as path
import sys, os, yaml, imp, re, logging
from collections import namedtuple
from iggytools.utils.util import mkdir_p, getUserHome, dict2namedtuple
from abc import ABCMeta, abstractmethod


class BaseToolPref:


    __metaclass__ = ABCMeta


    def __init__(self, iggytools_prefDir):  # Set prefdir location

        self.iggytools_prefDir = iggytools_prefDir


    @abstractmethod
    def getPreferences(self):
        pass

