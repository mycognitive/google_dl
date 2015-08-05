google_dl
========

Python script to download files via Google search.

Requirements
============

In order to use the script you need to install [Python 3.x](http://www.python.org/getit/) and the following packages:

- setuptools: https://pypi.python.org/pypi/setuptools#installation-instructions
- xgoogle: https://github.com/kenorb/xgoogle

For each package just run:

    py setup.py build
    py setup.py install

Disclaimer
==========

Before using, please read Google [Terms of Service](https://www.google.com/intl/en/policies/terms/)

> Don't misuse our Services.
> For example, don't interfere with our Services or
> try to access them using a method
> other than the interface and the instructions that we provide.

It is provided for personal study and research.

Usage
=====

    usage: google_dl.py [-?] [-v] [-d DEST] [-s SITE] [-f FILETYPE] [-x]
                        [-t TIMEOUT] [-m MAXRESULTS] [-p RESULTSPERPAGE]
                        query [query ...]

    positional arguments:
      query                 Query to search for.

    optional arguments:
      -?, --help            Show this help message and exit
      -v, --verbose         increase output verbosity.
      -d DEST, --download-dir DEST
                            Directory to download files.
      -s SITE, --site SITE  Site to search for.
      -f FILETYPE, --file-type FILETYPE
                            File type to download.
      -x, --force-directories
                            Create a hierarchy of directories based on the URL.
      -t TIMEOUT, --timeout TIMEOUT
                            Set socket read timeout for downloading in seconds
                            (float).
      -m MAXRESULTS, --max-results MAXRESULTS
                            Set maximum results to scrape.
      -p RESULTSPERPAGE, --results-per-page RESULTSPERPAGE
                            Set number of results per page.

License
=======
Licensed under MIT license.
