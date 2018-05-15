# CGSN Parsers

Python modules and shell script utilities used to parse the raw data files logged by the custom built CGSN data logger
systems. Resulting parsed data is saved in .JSON files for further processing, analysis and plotting.

The parsers convert the data from the different formats found in the raw log files (binary, ASCII, ASCIIHEX, mixed 
ASCII/binary) into a common format (JSON) that can be used for further processing and analysis. They do not convert the
data values (for the most part) found within the raw data. In other words, if a particular measurement contained in the 
raw data file is reported in counts, the parser does not convert that measurement to scientific units.

An exception to the above conversion applies to calculating an Epoch time stamp (seconds since 1970-01-01) from the date
and time string information contained in the files. The preferred source of time is the DCL timestamp as those systems
are synced to GPS via a LAN NTP server and are accurate to within a few milliseconds.

# Usage

Current usage is for monitoring the system health of the moorings (e.g. hydrogen concentration levels, battery voltages,
leak detect currents) and current environmental conditions (e.g. surface meteorological conditions, wave field and
subsurface currents) for deployment planning and troubleshooting (e.g. low salinity surface water from the Columbia 
River Plume may impact the ability of gliders to surface).

Several tools in multiple languages (a browser, Matlab, Python, R, Java, etc) exist that will enable a user to load a 
parsed JSON formatted data file for further processing and review.

This code is provided "as-is" for other users who may wish to interact directly with the
[raw data](https://rawdata.oceanobservatories.org/files/).

# Directory Organization

The python code for this project is available in the cgsn_parsers/parsers directory. Unit tests are available in the 
cgsn_parsers/tests directory.

Examples for how to work with some of the parsers are presented in the notebooks directory using 
[Jupyter](http://jupyter.org/) Notebooks.

Shell scripts in the utilities/harvesters directory are presented as examples of how to collect data from the different
instrument systems installed on a mooring, either individually or via a `master_harvester.sh` shell script. These 
scripts set the input and output directories for the data and call the appropriate python parser (located in the 
cgsn_parsers directory) to use with that instrument. It should be noted that these scripts were created with a specific 
user and system in mind. Others will need to adapt these scripts to fit their own needs.

# Requirements

This code was written and tested against Python 3.5.2 using Anaconda from [Continuum Analytics](https://www.continuum.io/).
The code has been used on Windows machines (7 and 10), as well as Linux servers running CentOS 6 and 7 and Debian 8.

The following additional python packages, beyond those provided by anaconda or miniconda are used
by this code:

   * nose (provided in anaconda)
   * numpy (provided in anaconda)
   * munch >= 2.1.0
   * pytz (provided in anaconda)

# Contributing

Users are encouraged to contribute to this code. The hope is this repository can provide the science community with a 
means of accessing and working with the raw OOI mooring data. To contribute, please fork the main 
[repo](https://bitbucket.org/ooicgsn/cgsn-parsers) to your own BitBucket account, create a branch, do your work, and 
then (when satisfied) submit a pull request to have your work integrated back into the main project repo.

This project uses [Semantic Versioning](https://semver.org/) with Major:Minor:Patch levels designtated in the VERSION
file. Be sure to include/update the version level as appropriate based on the guidlines for Semantic Versioning and
provide that information in the pull request so the project admin can appropriately tag the code for automated builds
and testing.

An example work flow would be:

```bash
# A git workflow template for working with the OOI CGSN Parsers repository.

# Create your development directories (just a guide, use your own directories)
mkdir -p ~/dev/code
cd ~/dev/code

# Fork the ooicgsn/cgsn-parsers repository to your account and clone a copy 
# of your fork to your development machine.
git clone git@bitbucket.org:<your_account>/cgsn-parsers.git
 
# The next steps must be completed in the local repository directory
cd cgsn-parsers
 
# Add the upstream feed for the master repository
git remote add upstream git@bitbucket.org:ooicgsn/cgsn-parsers.git
git fetch upstream

# Set the local master to point instead to the upstream master branch
git branch master --set-upstream-to upstream/master

# Keep your master branch updated, tied to the upstream master, and
# keep your remote fork in sync with the official repository (do this
# regularly)
git pull --ff-only upstream master
git push origin master

# Create your feature branch based off of the most recent version of the master
# branch by starting a new branch via...
#    git checkout master
#    git pull
#    git push origin master
# ... and then:
git checkout -b <branch>

### --- All of the next steps assume you are working in your <branch> --- ###
# Do your work, making incremental commits as/if needed, and back up to your
# bitbucket repository as/if needed.
while working == true
    git add <files>
    git commit -am "Commit Message"
    git push origin <branch>
end

# Before pushing your final changes to your repository, rebase your changes
# onto the latest code available from the upstream master.
git fetch upstream
git rebase -p upstream/master

# At this point you will need to deal with any conflicts, of which there should
# be none. Hopefully...

# Push the current working, rebased branch to your bitbucket fork and then 
# make a pull request to merge your work into the main code branch. Once the
# pull request is generated, add a comment with the following text:
#
#    @<code_admin> Ready for review and merge
#
# This will alert the main code admin to process the pull request.
git push -f origin <branch>
 
# At this point you can switch back to your master branch. Once the pull
# request has been merged into the main code repository, you can delete
# your working branches both on your local machine and from your bitbucket
# repository.
git checkout master
git pull
git push origin master
git branch -D <branch>
git branch -D origin/<branch>
```
