#! /usr/bin/env python

import subprocess, re
from optparse import OptionParser

def getCommandOutput(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  output = [line.replace("\n", "") for line in p.stdout.readlines()]
  p.wait()

  return output

import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


usage = "removeDPMDataset [datasetname] [publishingname]"
parser = OptionParser(usage)
parser.add_option("-n", "--dry-run", dest="dryrun",
                  help="Just list what we are supposed to do, but do not delete", action="store_true", default=False)
parser.add_option("-y", "", dest="yes",
                  help="Automatically answer yes to delete question", action="store_true", default=False)
#parser.add_option("-q", "--quiet",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

if len(args) != 2:
  parser.error("incorrect number of arguments (2 expected)")

datasetName_re = re.compile(args[0])
publishingName_re = re.compile(args[1])

dpmRoot = "/dpm/in2p3.fr/home/cms/data/store/user/sbrochet"

cmd = ["rfdir", dpmRoot]
datasets = getCommandOutput(cmd)

# Find a match for dataset name
for dataset in datasets:
  if dataset[0] != 'd':
    continue # It's not a folder

  # Extract real dataset name
  realDataset = dataset.split()[8]
  if datasetName_re.search(realDataset) is not None:
    #print "Looking inside '%s/%s'" %(dpmRoot, realDataset)
    cmd = ["rfdir", "%s/%s" % (dpmRoot, realDataset)]

    # Find a match for publish name
    publisheds = getCommandOutput(cmd)
    for published in publisheds:
      if published[0] != 'd':
        continue

      # Extract real publishing name
      realPublishing = published.split()[8]
      if publishingName_re.search(realPublishing) is not None:
        # We have a full match. Ask the user if he really want to remove this folder
        if options.dryrun:
          print("'%s/%s' would be deleted" % (realDataset, realPublishing))
        else:
          if options.yes or query_yes_no("Are you sure you want to remove '%s/%s'" % (realDataset, realPublishing), "no"):
            # Remove !
            print("Removing '%s/%s'" % (realDataset, realPublishing))
            cmd = ["rfrm", "-rf", "%s/%s/%s" % (dpmRoot, realDataset, realPublishing)]
            subprocess.call(cmd)

    # Check if the folder is empty
    cmd = ["rfdir", "%s/%s" % (dpmRoot, realDataset)]
    output = getCommandOutput(cmd)

    if len(output) == 0:
      if options.yes or query_yes_no("It seems that %s is empty. Remove it?" % (realDataset), "no"):
        # Nothing inside the folder, remove it
        cmd = ["rfrm", "-rf", "%s/%s" % (dpmRoot, realDataset)]
        subprocess.call(cmd)
