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


class StableVersion(Entity):
    version = Field(Unicode(10), primary_key=True, required=True)
    updated_on = Field(DateTime, default=datetime.datetime.now)
    template = "http://sourceforge.net/projects/nvda/files/releases/%(version)s/nvda_%(version)s_%(type)s.exe/download"

    def __repr__(self):
        return "<StableVersion: %s>" % self.version


    @property
    def installer_link(self):
        return self.template % {'version' : self.version, 'type' : 'installer'}

    @property
    def portable_link(self):
        return self.template % {'version' : self.version, 'type' : 'portable'}
