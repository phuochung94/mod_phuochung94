# -*- coding: utf-8 -*-
import armorshotanalyzer
from armorshotanalyzer.core import armorshotanalyzer_shell_info, armorshotanalyzer_hooks

def init():
    try:
        armorshotanalyzer_shell_info.install()
        armorshotanalyzer_hooks.install()
    except Exception:
        fini()
        raise

def fini():
    try:
        armorshotanalyzer_hooks.uninstall()
    finally:
        armorshotanalyzer_shell_info.uninstall()

init()

from armorshotanalyzer.debug import log
log("Loaded")
