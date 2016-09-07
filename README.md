# nodejs2rpm
Instantly generate valid RPM SPECs for packaging NodeJS modules

# a little history

I created this script in order to automate the process of packaging NodeJS modules in OBS (Open Build Service -- http://build.opensuse.org). 

NodeJS modules were made to be installed directly from the web, but if you ever maintained a distro in any business context, you know that a lot of times you WON'T have an external internet connection. So, in order to keep the distribution (and a lot of people) happy, I made this script. 

I based my work on Marguerite Su's methodology described here: https://en.opensuse.org/openSUSE:Packaging_nodejs

However, I added a few tweaks to allow the module to be properly registered with NPM (NodeJS Package Manager), and a generic SPEC skeleton that can be adapted for 95% of the modules.

# how it works

Basically, it downloads the JSON containing a specific module metadata, parses it and fills a SPEC template with the basic information. 
It also has a little intelligence:
 * it properly create "Requires:" directives based on the dependencies
 * it downloads and analyzes the tarball to find out the README.md file name and sets it accordingly in the SPEC as a %doc
 * there are a few options to customize some aspects, like changelog messages, etc.
 * it creates OBS-compliant "changes" files.

# how to use

Just run "python nodejs2rpm.py -h" and have a look at the options. The defaults should work for most people.

For every module you run this script on, a new directory named "nodejs-<MODULE>" will be created.

# quick tips

You can create SPECS for a ton of modules at once in just one line, like this:

  # for f in code hoek prr errno; do python -m $f -e my@email.com -c "New package"; done

Have fun!

