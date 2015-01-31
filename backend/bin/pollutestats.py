#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys

from storm.locals import create_database, Store
from copy import copy

from globaleaks import models
from globaleaks.utils.utility import randint, datetime_now, utc_past_date

DEFAULT_OUTPUT_DBNAME = "/tmp/cleaned_glbackend.db"
DUMMY_UNICODE_TEXT = u"¹²³ HelLlo! I'm the Batman"

def _fancy_print(tablename, elements=0):
    if elements:
        print u' ¬æ  %d elements exported from %s' %\
              (elements, tablename)
    else:
        print u' ¬æ  exported %s' % tablename


_uuid_track = {}
_incremental_counter = 1

def _change_tracking_uuid(sourceuuid):
    """
    @param sourceuuid: one of the UUID used in the node
    @return: an incremental unsafe UUID, the same UUID is returned
        from the same source

    r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
    A000A000-0000-0000-0000- [ 12 number ]

    """
    global _incremental_counter

    def create_uuid(incremental_number):
        numstr = "%s" % incremental_number
        retstr = "A000A000-0000-0000-0000-%s%s" % (
            ((12 - len(numstr)) * "0"), numstr
        )
        return unicode(retstr)

    if not _uuid_track.has_key(sourceuuid):
        _uuid_track[sourceuuid] = _incremental_counter
        _incremental_counter += 1

    return create_uuid(_uuid_track[sourceuuid])


def do_storm_copy(source_store_obj):
    thecopy = source_store_obj.__class__()

    for k, v in source_store_obj._storm_columns.iteritems():
        setattr(thecopy, v.name, getattr(source_store_obj, v.name) )

    return thecopy


def do_statspollute(dbfile):

    # source
    gl_database = create_database("sqlite:%s" % dbfile)
    source_store = Store(gl_database)

    stats = source_store.find(models.Stats)

    counter = 0
    for s in stats:
        source_store.remove(s)
        counter += 1

    print "removed %d entry in stats" % counter

    counter = 0
    # 21 days in the past
    for past_hours in xrange(24 * 7 * 3):
        past_hours += 4
        when = utc_past_date(hours=past_hours)

        newstat = models.Stats()
        newstat.freemb = randint(1000, 1050)
        newstat.year = when.isocalendar()[0]
        newstat.week = when.isocalendar()[1]

        level = round( (randint(0, 1000) / 240.0), 1) - 2
        activity_fake = {
            'logins_successful' : int(randint(0,11) + (5 * level)),
            'logins_failed': int(randint(0, 11) + (5 * level)),
            'wb_comments': int(randint(0,11) + (5 * level)),
            'wb_messages': int(randint(0,11) + (5 * level)),
            'uploaded_files': int(randint(0,11) + (5  * level)),
            'appended_files': int(randint(0,11) + (5 * level)),
            'submissions_started': int(randint(0,11) + (5 * level)),
            'submissions_completed': int(randint(0,11) + (5 * level)),
            'receiver_comments': int(randint(0,11) + (5 * level)),
            'receiver_messages': int(randint(0,11) + (5 * level))
        }

        for k, v in activity_fake.iteritems():
            if v < 0:
                activity_fake[k] = 0

        newstat.start = when
        newstat.summary = activity_fake
        counter += 1
        source_store.add(newstat)

    print "Committing %d stats" % counter
    source_store.commit()


def funny_print(stringz, details):

    block = 40
    print stringz, " " * (block - len(stringz)), details

def check_file(isafile):
    print "checking file: %s" % isafile
    if not os.path.isfile(isafile):
        print "Missing file: %s" % isafile
        quit()

if len(sys.argv) == 1:
    print "python pollutestats.py workingdir/db/glbackend-1?.db"
    print "←shall the spirit of the holy fucking cow protect you→"
    quit(0)

print "←shall the spirit of the holy fucking cow protect you→"
print "                       ←Start!→"
print ""
check_file(sys.argv[1])
# if 'print' is present, or something else, just dump to stdout
do_statspollute(sys.argv[1])
