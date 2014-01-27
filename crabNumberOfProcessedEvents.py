#!/usr/bin/env python

import sys, os, glob
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

def readXMLPublish(tree, getFiltered):
  if tree.getroot().attrib["Status"] != "Success":
    return True, 0

  if not getFiltered:
    p = tree.findall("InputFile/EventsRead")
    if (p is None):
      sys.stderr.write("Error: Malformed XML file '%s'\n" % xml)
      return False, 0

    totalEvents = 0
    for events in p:
      totalEvents += int(events.text.strip(" \t\n\r"))

    return True, totalEvents
  else:
    p = tree.find("File/TotalEvents")
    if p is None:
      sys.stderr.write("Error: Malformed XML file '%s'\n" % xml)
      return False, 0

    return True, int(p.text.strip(" \r\n\t"))

from optparse import OptionParser
parser = OptionParser("usage: %prog [options] crab_folder")
parser.add_option("", "--filtered", action="store_true", dest="filtered", default=False, help="Output the number of filtered events instead of the number of processed events")
(options, args) = parser.parse_args()

if len(args) != 1:
  parser.error("Incorrect number of arguments")

input = args[0]

if (not os.path.exists(input + "/res")):
  exit("'%s/res/' does not exists" % input);

path = "%s/%s/res" % (os.getcwd(), input);

exitCode = 0
totalEvents = 0
for file in glob.glob("%s/*.xml" % path):
  tree = ElementTree();
  try:
    tree.parse(file)
    ok,events = readXMLPublish(tree, options.filtered)

    if (not ok):
      exitCode=1
      continue

    totalEvents += events

  except IOError:
    sys.stderr.write("Warning: can't open '%s'\n" % file)
    exitCode = 1
  except ExpatError:
    sys.stderr.write("Warning: malformed XML file '%s'\n" % file);
    exitCode = 1

print(totalEvents)
exit(exitCode)
