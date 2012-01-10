import datetime
import logging
import os
import os.path
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
	type char(10),
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
