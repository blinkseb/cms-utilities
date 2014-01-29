#!/usr/bin/env python

import os,sys
from optparse import OptionParser
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

def readXMLAnalysis(tree):
  p = tree.find("AnalysisFile/LFN")
  if (p is None):
    sys.stderr.write("Error: Malformed XML file '%s' (AnalysisFile/LFN is missing)\n" % xml)
    return False,""
  if (not ("Value" in p.attrib)):
    sys.stderr.write("Error: Malformed XML file '%s' (AnalysisFile/LFN is missing attribute 'Value')\n" % xml)
    return False,""

  return True,p.attrib["Value"]

def readXMLPublish(tree):
  p = tree.find("File/LFN")
  if (p is None):
    sys.stderr.write("Error: Malformed XML file '%s' (File/LFN is missing)\n" % xml)
    return False,""

  return True,p.text.strip(" \t\n\r");

parser = OptionParser()
parser.add_option("", "--rfio", dest="rfio", action="store_true", help="Make URL compatible with RFIO protocol", default=False)
parser.add_option("", "--xrootd",  action="store_true", dest="xrootd", default=False, help="Make URL compatible with XrootD protocol")
parser.add_option("", "--check",  action="store_true", dest="check", default=False, help="Check if file exist")
parser.add_option("", "--publish",  action="store_true", dest="publish", default=False, help="Analysis / Publish mode")

(options, args) = parser.parse_args()

input = args[0];
job_type = "publish" if options.publish == True else "analysis"

if (job_type != "analysis") and (job_type != "publish"):
  exit("Unknown job type %r. Must be either 'analysis' or 'publish'" % job_type);

appendRFIO = options.rfio
appendXROOTD = options.xrootd
  
# if true, check with rfdir if the file exists
checkRFIO = options.check

isCERN = os.system("uname -n | grep cern &> /dev/null") == 0;
if (isCERN):
  lfnPrefix = "/castor/cern.ch%s";
  xrootdPrefix = ""
else:
  lfnPrefix = "/dpm/in2p3.fr/home/cms/data%s";
  xrootdPrefix = "root://lyogrid06.in2p3.fr/"

if (not os.path.exists(input + "/res")):
  exit("'%s/res/' does not exists" % input);

path = "%s/res" % (input);
files = os.listdir(path)

if len(files) == 0:
  exit(1)

exitCode = 0
for file in files:
  root, extension = os.path.splitext(file);
  if (extension != ".xml"):
    continue;
  xml = "%s/%s" % (path, file)
  tree = ElementTree();
  try:
    tree.parse(xml)
    if (job_type == "analysis"):
      ok,lfn = readXMLAnalysis(tree)
    else:
      ok,lfn = readXMLPublish(tree)
    if (not ok):
      exitCode=1
      continue

    absoluteLFN = lfnPrefix % lfn;

    if (checkRFIO):
      exists = os.system("rfdir \"%s\" &> /dev/null" % absoluteLFN);
      if (exists != 0):
        sys.stderr.write("[%s] Error: file %s does not exists. Skipping it.\n" % (input, absoluteLFN));
        exitCode = 1
        continue;
    if (appendRFIO):
      print "rfio://%s" % (absoluteLFN)
    elif appendXROOTD:
      print xrootdPrefix + absoluteLFN
    else:
      print "%s" % (absoluteLFN)

  except IOError:
    sys.stderr.write("Warning: can't open '%s'\n" % xml)
    exitCode = 1
  except ExpatError:
    sys.stderr.write("Warning: malformed XML file '%s'\n" % xml);
    exitCode = 1

exit(exitCode)
