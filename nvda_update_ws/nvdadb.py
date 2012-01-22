import datetime
import logging
import os
import os.path
import re
import urllib2
import web

log = logging.getLogger(__name__)

_tables_sql = [
"drop table if exists snapshots;",
"""
create table snapshots(
	branch varchar(30) unique not null primary key,
	revision int,
	active bool default 't',
	updated_on timestamp);
""",
"drop table if exists versions;",
"""
create table versions(
	version varchar(30) unique not null primary key,
	stability char(10),
	date timestamp);
"""]

_dbname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite3')
_db = None

def init(create=False):
    global _db
    _db = web.database(dbn="sqlite", db=_dbname)
    if create:
        for stm in _tables_sql:
            _db.query(stm)


def create_snapshot_branch(branch):
    _db.insert("snapshots", branch=branch)

def update_snapshot_branch(branch, revision):
    _db.update("snapshots", "branch=$branch", vars=locals(),
        revision=revision, updated_on=datetime.datetime.now())
        
def get_last_snapshot(branch):
    return Snapshot(**_db.where("snapshots", branch=branch)[0])

def get_snapshot_branches():
    return (Snapshot(row) for row in _db.select("snapshots"))

def create_version(version, stability='stable'):
    v = NVDAVersion(version=version)
    _db.insert("versions", version=version, stability=v['stability'], date=datetime.datetime.now())

def delete_version(version):
    _db.delete('versions', version=version)

def get_version(version):
    rows = _db.where("versions", version=version)
    return NVDAVersion(**rows[0])

def get_latest_version(stabilities=['stable']):
    versions = [NVDAVersion(**row) for row in _db.select('versions', where="stability in(" + ", ".join(["'" + s + "'" for s in stabilities]) + ')')]
    s = sorted(versions, reverse=True)
    return versions[0] if versions else None

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


class Snapshot(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        template = "http://www.nvda-project.org/snapshots/%(branch)s/nvda_snapshot_%(branch)s-%(revision)d_%(type)s.exe"
        self['portable'] = template % dict(type='portable', **self)
        self['installer'] = template % dict(type='installer', **self)



def cron_update_snapshots():
    branches = [b for b in _db.select("snapshots", where="active = 't'")]
    template = "http://www.nvda-project.org/snapshots/%s/.last_snapshot"
    for b in branches:
        try:
            new_revision = int(urllib2.urlopen(template % b.branch).read())
            if new_revision != b.revision:
                update_snapshot_branch(b.branch, new_revision)
                log.info("Branch %s updated to %d" % (b.branch, new_revision))
        except Exception, e:
            log.exception(e)


if __name__ == '__main__':
    init()
    cron_update_snapshots()
