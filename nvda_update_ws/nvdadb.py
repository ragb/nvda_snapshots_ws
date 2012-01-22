import datetime
import logging
import os
import os.path
import re
import urllib2
from elixir import *

log = logging.getLogger(__name__)



_dbname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite3')
metadata.bind = "sqlite:///%s" % _dbname
metadata.bind.echo = True

def init(create=False):
    setup_all(True)




class NVDAVersion(dict):
    stabilities = {'beta' : 1, 'rc' : 2, 'stable' : 3}
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        # parce version (use regexp instead?)
        self._parts = self['version'].split('.')
        self._testing = (self.stabilities['stable'], 0)
        for t in NVDAVersion.stabilities.keys():
            if t in self._parts[-1]:
                tmp = self._parts[-1].split(t)
                self._testing = (self.stabilities[t], int(tmp[1]))
                self._parts[-1] = tmp[0]
        self._parts = [int(p) for p in self._parts]
        self['stability'] = self._testing[0]
        # create links
        template = "http://sourceforge.net/projects/nvda/files/releases/%(version)s/nvda_%(version)s_%(type)s.exe/download"
        self['installer'] = template % dict(type='installer', **self)
        self['portable'] = template % dict(type='portable', **self)

    def __cmp__(self, other):
        l = min(len(self._parts), len(other._parts))
        for i in range(l):
            r = self._parts[i] - other._parts[i]
            if r != 0:
                return r
        return (len(self._parts) - len(other._parts)) \
        or (self._testing[0] - other._testing[0])\
        or (self._testing[1] - other._testing[1])


class Snapshot(Entity):
    branch = Field(Unicode(30), primary_key=True, required=True)
    revision = Field(Integer)
    active = Field(Boolean, default=True)
    uppdated_on = Field(DateTime, default=datetime.datetime.now)
    template = "http://www.nvda-project.org/snapshots/%(branch)s/nvda_snapshot_%(branch)s-%(revision)d_%(type)s.exe"
    def __unicode__(self):
        return "<%s: %s>" % (self.__name___, self.branch)

    @property
    def portable_link(self):
        return self.template % dict(type='portable', **self.to_dict())

    @property
    def installer_link(self):
        return self.template % dict(type='installer', **self.to_dict())


