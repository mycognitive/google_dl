#!/usr/bin/env python3
# Sample usage:
#   ./google_dl.py foo bar
#   ./google_dl.py -s http://example.com -f pdf foo bar
#   ./google_dl.py "foo bar site:http://example.com filetype:pdf"

import os, sys
import argparse
import urllib.request
from urllib.error import URLError, HTTPError, ContentTooShortError
from xgoogle.search import GoogleSearch, SearchError
import re
import socket
import mimetypes

class GoogleDl():
    def __init__(self, query, filetypes, site, resultsperpage, maxresults):
        if filetypes:
            filetypes = re.split(",", filetypes)
            query += " filetype:" + filetypes.pop(0)
            for filetype in filetypes:
                query += " OR filetype:" + filetype

        if site:
            query += " site:" + site

        print(query)
        self.gs = GoogleSearch(query, random_agent=True)
        self.gs.results_per_page = int(resultsperpage)
        self.maxresults = int(maxresults)
        self.lastpage = False

    def getTotal(self):
        return len(self.results)


    def dlFileOld(self, url, path):
        try:
            urllib.request.urlretrieve(url, filename=path)
        except HTTPError as err:
            print("Error: %s, reason: %s." % (err.code, err.reason))
            return False
        except ContentTooShortError as err:
            print("Error: The downloaded data is less than the expected amount, so skipping.")
            return False
        except urllib.error.URLError:
            print("Error: Reading socket timed out, try again later.")
            return False


    def dlFile(self, url, path):
        request = urllib.request.Request(url, headers={"User-Agent": self.gs.browser.get_user_agent()})
        try:
            with urllib.request.urlopen(request) as i, open(path, "wb") as o:
                o.write(i.read())
        except URLError:
            print("Error: Reading socket timed out, try again later.")
            return False
        except HTTPError as err:
            print("Error: %s, reason: %s." % (err.code, err.reason))
            return False
        except ContentTooShortError as err:
            print("Error: The downloaded data is less than the expected amount, so skipping.")
            return False
        except OSError as err:
            print("Error: %s raised when tried to save the file '%s'" % (err.strerror, err.filename))
            sys.exit(1)


    def __iter__(self):
        self.count = 0
        return self


    def __next__(self):
        if self.lastpage or self.count >= self.maxresults:
            raise StopIteration

        results = self.gs.get_results()

        if not results:
            raise StopIteration
        if len(results) < self.gs.results_per_page:
            self.lastpage = True

        self.count += len(results)
        return results


def get_path_via_url(url, dest = ".", dirs = False):
    # Decode URL, use path part, strip its head & tail
    path = urllib.parse.unquote(urllib.parse.urlparse(url)[2]).strip("/")
    if path is "":
        pseudoPath = urllib.parse.unquote(urllib.parse.urlparse(url)[1])
    else:
        pseudoPath = ""

    # Destination dir must have a trailing slash
    if not dest.endswith("/"):
        dest += "/"

    # Check whether URL ends with an extension, so we should gather MIME info from response header or not
    extension = re.search("\.(\w+)$", path)
    if extension is None or pseudoPath is not "":
        request = urllib.request.Request(url, method="HEAD")
        try:
            response = urllib.request.urlopen(request)
            mimetype = re.search("(\w+/\w+)", dict(response.getheaders())["Content-Type"])
            if mimetype is not None:
                path += pseudoPath + mimetypes.guess_extension(mimetype.group(1))
            else:
                path += pseudoPath + ".html"
        except BaseException:
            path += pseudoPath + ".html"

    if dirs:
        return dest + path
    else:
        # Return only the last element from the '/' delimeted path list
        return dest + re.split("/", path)[-1]


if __name__ == "__main__":
    # Parse arguments.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-?", "--help",
        action="help", help="Show this help message and exit")
    parser.add_argument("-v", "--verbose",
        action="store_true", dest="verbose", help="increase output verbosity.")
    parser.add_argument("-d", "--download-dir",
        action="store",      dest="dest", help="Directory to download files.", default=".")
    parser.add_argument("-s", "--site",
        action="store",      dest="site", help="Site to search for.", default=None)
    parser.add_argument("-f", "--file-type",
        action="store",      dest="filetype", help="Comma-separated list of file types to download.", default=None)
    parser.add_argument("-x", "--force-directories",
        action="store_true",      dest="dirs", help="Create a hierarchy of directories based on the URL.")
    parser.add_argument("-t", "--timeout",
        action="store",      dest="timeout", help="Set socket read timeout for downloading in seconds (float).", default=None)
    parser.add_argument("-m", "--max-results",
        action="store",      dest="maxresults", help="Set maximum results to scrape.", default=1000)
    parser.add_argument("-p", "--results-per-page",
        action="store",      dest="resultsperpage", help="Set number of results per page.", default=50)
    parser.add_argument("query", nargs="+", help="Query to search for.")

    # Build query string
    args = parser.parse_args()
    query = " ".join(args.query)

    # Set timeout if there's any
    if args.timeout:
        socket.setdefaulttimeout(float(args.timeout))

    # Download if doesn't exist locally
    try:
        page = GoogleDl(query, args.filetype, args.site, args.resultsperpage, args.maxresults)
        #print("Query: %s" % (query) if args.verbose else "")
        i = 1
        for results in page:
            print("Trying to download results from page #%d  (results %d-%d)" % (i, (i - 1)*page.gs.results_per_page + 1, min(i*page.gs.results_per_page, (i - 1)*page.gs.results_per_page + len(results))))
            for result in results:
                url = result.getURL()
                path = get_path_via_url(url, args.dest, args.dirs)
                filename = os.path.basename(path)
                dirname = os.path.dirname(path)
                os.makedirs(dirname, 0o755, True)
                print("Downloading '%s' from '%s' into %s..." % (filename, url, dirname))
                if os.path.isfile(path):
                    print("File '%s' already exists, skipping." % (path))
                else:
                    page.dlFile(url, path)
            i += 1
            print("")

    except KeyboardInterrupt:
        sys.exit()
    except SearchError as err:
        print("Search failed: %s" % (err))
