#!/usr/bin/python
import sys
import json
import requests
import re
from optparse import OptionParser
import pdb
import os
import tarfile
import shutil
import time
import locale
import codecs
import jinja2

def is_string(obj):
    try:
        obj + ''
        return True
    except TypeError:
        return False


def fillChanges(email, message, output):
    # set the locate to english
    locale.setlocale(locale.LC_TIME, "en_US")

    # create a RPM-compatible timestamp
    timestamp = time.strftime("%a %b %d %H:%M:%S %Z %Y - " + email, time.localtime())

    out = open(output + '.changes', "w")
    out.write('-------------------------------------------------------------------')
    out.write('\n')
    out.write(timestamp)
    out.write('\n\n')
    out.write('- ' + message)
    out.write('\n\n')
    out.close()


def getREADME(tar_file):

    print "Using tarfile: " + tar_file
    if not tarfile.is_tarfile(tar_file):
        print "Invalid tar file!"
        sys.exit(1)

    tar = tarfile.open(tar_file, "r:gz")
    docfile = "none"
    for tarinfo in tar:
        if (tarinfo.isreg()) and (re.search('.*readme.md$', tarinfo.name, re.I) is not None):
            print "Found README - " + os.path.basename(tarinfo.name)
            docfile = os.path.basename(tarinfo.name)
    tar.close()
    return docfile

def getLICENSE(tar_file):

    print "Using tarfile: " + tar_file
    if not tarfile.is_tarfile(tar_file):
        print "Invalid tar file!"
        sys.exit(1)

    tar = tarfile.open(tar_file, "r:gz")
    licensefile = "none"
    for tarinfo in tar:
        if (tarinfo.isreg()) and (re.search('.*license$', tarinfo.name, re.I) is not None):
            print "Found LICENSE - " + os.path.basename(tarinfo.name)
            licensefile = os.path.basename(tarinfo.name)
    tar.close()
    return licensefile


def fillSPEC(template_file, sub_dict, docfile, licensefile, output_file):


    # Initialize the Jinja environment
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(options.templatedir))

    template = env.get_template(template_file)
    result = template.render(sub_dict).encode('utf-8')                          # render template and encode properly

    output_file = output_file + '.spec'
    print "Using template: " + template_file
    print "Output will be: " + output_file
    outfile = open(output_file, 'wb')                                     # write result to spec file
    try:
        outfile.write(result)
    finally:
        outfile.close()

    print "SPEC done."


# main program
parser = OptionParser(version="%prog 1.0")
parser.add_option("-m", "--module", type="string", dest="module",
                  metavar="NODEJSMODULE", help="name of the NodeJS module")
parser.add_option("-t", "--template", type="string", dest="templatefile",
                  help="name of the SPEC template file to use",
                  metavar="SPECTEMPLATE", default="default.spec")
parser.add_option("-T", "--templatedir", type="string", dest="templatedir",
                  help="name of the SPEC template directory to use",
                  metavar="SPECTEMPLATEDIR", default="/usr/share/nodejs2rpm/templates")
parser.add_option("-f", "--overwrite", action="store_true", dest="overwrite",
                  help="overwrite the destination directory")
parser.add_option("-e", "--email", type="string", dest="email",
                  help="define the email address for changelog entries",
                  metavar="USER@DOMAIN", default="somewhere@overtherainbow")
parser.add_option("-c", "--changelog", type="string", dest="changelog",
                  help="define the changelog message to be generated in a corresponding <module>.changes file",
                  metavar="MESSAGE", default="Initial build from autogenerated SPEC.")
parser.add_option("-b", "--boilerplate", type="string", dest="boilerplate",
                  help="define the boilerplate message to be added as a description",
                  metavar="MESSAGE", default="NodeJS module.")

(options, args) = parser.parse_args()

if options.module is None:
    print "Must supply module name!"
    sys.exit(1)

outdir = "nodejs-" + options.module + "/"
output = outdir + 'nodejs-' + options.module
baseurl = "http://registry.npmjs.org/"

# this is the text that will be appended to every package description
boilerplate = options.module + " is a NodeJS module."

# download the package JSON from registry.npmjs.org
print "Downloading metadata from " + baseurl + options.module + "..."
r = requests.get(baseurl + options.module)
if r.status_code is not requests.codes.ok:
    print "Error while downloading the metadata for module " + options.module
    + " from " + baseurl + "."
    print "Status code: " + r.raise_for_status()
    sys.exit(1)

metadata = r.json()

if metadata is not None:
    meta_name = metadata['name']
    meta_desc = metadata['description'].rstrip('.')  # remove the trailing dot to avoid a "summary ends in a dot"  OBS warning
    meta_latest = metadata['dist-tags']['latest']
    meta_versions = metadata['versions']
    if 'repository' not in meta_versions[meta_latest]:
        meta_dist_url = "UNKNOWN FIXME!"
    else:
        meta_dist_url = meta_versions[meta_latest]['repository']['url']
    meta_dist_tarball = meta_versions[meta_latest]['dist']['tarball']
    meta_dist_sha1 = meta_versions[meta_latest]['dist']['shasum']

    # pdb.set_trace()
    if 'license' in meta_versions[meta_latest]:
        if 'type' in meta_versions[meta_latest]['license']:
            meta_license = meta_versions[meta_latest]['license']['type']
        else:
            meta_license = meta_versions[meta_latest]['license']
    elif 'license:' in meta_versions[meta_latest]:
        meta_license = meta_versions[meta_latest]['license:'][0]['type']
    elif 'licenses' in meta_versions[meta_latest]:
        if is_string(meta_versions[meta_latest]['licenses']):
            meta_license = meta_versions[meta_latest]['licenses']
        else:
            meta_license = meta_versions[meta_latest]['licenses'][0]['type']
    else:
        # according to https://help.github.com/articles/open-source-licensing/,
        # code published on GITHUB without a defined license is considered
        # proprietary.
        meta_license = 'Proprietary'

    if 'dependencies' not in meta_versions[meta_latest]:
        meta_dependencies = []
    else:
        meta_dependencies = meta_versions[meta_latest]['dependencies']

    if 'devDependencies' not in meta_versions[meta_latest]:
        meta_dev_dependencies = []
    else:
        meta_dev_dependencies = meta_versions[meta_latest]['devDependencies']

else:
    print 'Error extracting metadata.'
    sys.exit(1)

print "Parsing metadata..."
print
print "name: ", meta_name
print "description: ", meta_desc
print "license: ", meta_license
print "latest: ", meta_latest

# print meta_versions[meta_latest]
print "version ", meta_latest
print "latest URL: ", meta_dist_url
print "tarball: ", meta_dist_tarball
print "sha1: ", meta_dist_sha1

for f in meta_dependencies:
    print "dependency: ", f, " minversion: ", meta_dependencies[f]



# if overwrite is on, remove the directory first
if options.overwrite is True:
    shutil.rmtree(outdir, True)

# create the destination directory
try:
    os.mkdir(outdir)
except IOError:
    print 'Error creating directory!'
    sys.exit(1)


# download the tarball
print "Downloading tarball from " + meta_dist_tarball + "..."
r = requests.get(meta_dist_tarball)
if r.status_code is not requests.codes.ok:
    print "Error while downloading the tarball from " + meta_dist_tarball + "."
    print "Status code: " + r.raise_for_status()
    sys.exit(1)

# write the tarball
tarball = outdir + os.path.basename(meta_dist_tarball)
out = open(tarball, "w")
out.write(r.content)
out.close()

# get the README file from the tar
docfile = getREADME(tarball)

# get the LICENSE file from the tar
licensefile = getLICENSE(tarball)

# map the strings to the values to be substituted
sub_dict = {
    '__VERSION__': meta_latest,
    # OBS considers a lowercase first letter in the summary a fatal error. Really!
    '__SUMMARY__': meta_desc.capitalize(),
    '__LICENSE__': meta_license,
    '__URL__': meta_dist_url,
    '__BASENAME__': meta_name,
    '__REQUIRES__': meta_dependencies,
    '__DOC__': docfile,
    '__LICENSEF__': licensefile,
    '__BOILERPLATE__': boilerplate,
    # the metadata does not have a detailed description
    '__DESCRIPTION__': meta_desc }

# substitute the variables in the SPEC template
fillSPEC(options.templatefile, sub_dict, docfile, licensefile, output)

# create the changes file if requested
fillChanges(options.email, options.changelog, output)

print "Done! Have fun with your new package!"
sys.exit(0)

