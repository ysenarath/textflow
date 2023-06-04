"""Configuration for the textflow package.

This module contains the configuration for the textflow package.

Attributes
----------
config : configparser.ConfigParser
    Configuration for the textflow package.
"""
import configparser
import os

__all__ = [
    'config',
]

PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()

config.read_dict({
    'textflow': {
        'package_path': PACKAGE_PATH,
        'autobuild': False,
    },
})
