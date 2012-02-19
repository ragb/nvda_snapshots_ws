# snapshotVersionChecker.py
# Version 1.1
# NVDA plugin to check if we are running the last available snapshot.
# copyright (c) 2011 - Rui Batista <ruiandrebatista@gmail.com>
#
# This code is subject to the same terms as the NVDA Screen Reader
import gettext
import os.path
import re
import threading
import urllib
import webbrowser
import wx

import config
import globalPluginHandler
import globalVars
import gui
import languageHandler
from logHandler import log
import ui
import versionInfo

__author__ = "Rui Batista"
__version__ = "1.1"

# Make gettext available in this module using a different domain
_basePath = os.path.dirname(os.path.abspath(__file__))
_localedir = os.path.join(_basePath, "locale")
_ = gettext.translation('snapshotVersionChecker', localedir=_localedir, languages=[languageHandler.curLang]).ugettext

_snapshot_url_template = "http://www.nvda-project.org/snapshots/%(branch)s/nvda_snapshot_%(branch)s-%(revision)d_%(type)s.exe"

def _make_snapshot_url(branch, revision, type):
	return _snapshot_url_template % {'branch' : branch, 'revision' : revision, 'type' : type}

def _nvda_copy_type():
	return "installer" if config.isInstalledCopy() else "portable"


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	""" Plugin to check if a NVDA snapshot is the last available version.

	At NVDA startup the plugin checks if there is a new snapshot available and
	asks the user if he wants to go to the snapshots
	web page to download it.
	TODO: download the new snapshot in the plugin itself in the future."""

	regexp = re.compile(r"^(bzr-)?(\w+)-(\d+)$")

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		# if this is a secure instance (login, UAC previleged, etc, don't bother the user)
		if globalVars.appArgs.secure:
			return

		# find if we are running a snapshot:
		self._current_version = None
		self._branch = None
		self._next_version = None
		m = GlobalPlugin.regexp.match(versionInfo.version)
		if m is not None:
			self._branch = m.group(2)
			self._current_version = int(m.group(3))
			log.debug("Running a snapshot. Spawning thread to check latest version.")
			self._thread = threading.Thread(target=self._update_next_version)
			self._thread.setDaemon(True)
			self._thread.start()

	def _update_next_version(self):
		template = "http://www.nvda-project.org/snapshots/%s/.last_snapshot"
		url = template % self._branch
		log.debug("Reading latest version from %s", url)
		self._next_version = int(urllib.urlopen(url).read())
		if self._next_version <= self._current_version:
			log.info("Snapshot up to date at revision %d", self._current_version)
		else:
			# run the update on the main thread:
			log.info("Branch %s as a new snapshot with revision %d", self._branch, self._next_version)
			wx.CallAfter(self._ask_for_update)

	def _ask_for_update(self):
		if gui.messageBox(_("""NVDA %(branch)s revision %(next)d is available. You are still running revision %(current)d.
Do you want to download the last snapshot from the web page?
""") % {"branch": self._branch, "next" : self._next_version, "current" : self._current_version},
		caption=_("New snapshot Available."), style=wx.YES_NO|wx.ICON_WARNING) == wx.YES:
			ui.message(_("Opening Snapshots web page."))
			url = _make_snapshot_url(self._branch, self._next_version, _nvda_copy_type())
			log.debug("Openning browser: %s.", url)
			webbrowser.open(url)
