import os
import sys


if sys.platform.startswith('win'):
    config_dir = os.path.expanduser(os.path.join("~", ".sirsim"))
    cache_dir = os.path.join(config_dir, "cache")
else:
    config_dir = os.path.expanduser(os.path.join("~", ".config", "sirsim"))
    cache_dir = os.path.expanduser(os.path.join("~", ".cache", "sirsim"))

decoder_cache_dir = os.path.join(cache_dir, "decoders")
install_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
examples_dir = os.path.join(install_dir, "docs", "examples")

sirsimrc = {'system': os.path.join(install_dir, 'sirsim-data', 'sirsimrc'),
           'user': os.path.join(config_dir, "sirsimrc"),
           'project': os.path.abspath(os.path.join(os.curdir, "sirsimrc"))}
