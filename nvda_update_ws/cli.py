import cmd
import logging
import sys
from nvdadb import *

log = logging.getLogger(__name__)

class NVDACmd(cmd.Cmd):
    prompt = ">>> "

    def do_update_snapshots(Self, line):
        """ Updates all active snapshot branches. """
        branches = Snapshot.query.all()
        template = "http://www.nvda-project.org/snapshots/%s/.last_snapshot"
        for b in branches:
            try:
                new_revision = int(urllib2.urlopen(template % b.branch).read())
                if new_revision != b.revision:
                    b.revision = new_revision
                    b.updated_on = datetime.datetime.now()
                    session.commit()
                    log.info("Branch %s updated to %d" % (b.branch, new_revision))
            except Exception, e:
                log.exception(e)

    def do_create_snapshot_branch(self, line):
        """ Creates a new snapshot branch """
        s = Snapshot(branch=line.strip())
        session.commit()
        log.info("Created snapshot branch %s.", s.branch)

    def do_snapshot_revision(self, line):
        """ Gets the revision for a snapshot branch """
        s = Snapshot.query.filter_by(branch=line.strip()).first()
        print s.revision

    def do_quit(self, line):
        """ Exits the command line interface. """
        sys.exit(0)
    do_exit = do_quit

if __name__ == '__main__':
    init()
    NVDACmd().cmdloop()
