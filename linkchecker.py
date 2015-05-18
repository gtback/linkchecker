#!/usr/bin/env python

"""
Usage: python linkchecker.py http://localhost:4000 > res.txt
"""

import sys
from urlparse import urlsplit, urljoin

from bs4 import BeautifulSoup
import requests


def main():
    root_url = sys.argv[1]

    print root_url
    LinkChecker(root_url).check_links(max_levels=1)


class LinkChecker(object):

    def __init__(self, root_url):
        self.root_url = root_url

        parsed = urlsplit(root_url)

        self.scheme = parsed.scheme
        self.netloc = parsed.netloc

        self._pending_links = []
        self._origin_urls = {self.root_url: "ORIGIN"}

    def check_links(self, max_levels=None):
        self.parse_page(self.root_url)

        # for i in list(self._pending_links):
        #     self.parse_page(i)

        while self._pending_links:
            # Copy list so as to not mutate it in place
            for i in list(self._pending_links):
                self._pending_links.remove(i)
                self.parse_page(i)

    def parse_page(self, url):
        r = requests.get(url, proxies={"http":""})

        # TODO: deal with redirects
        if r.status_code != requests.codes.ok:
            print r.status_code, self._origin_urls[url], "->", url
            return
        page = r.text

        soup = BeautifulSoup(page)
        for link in soup.find_all('a'):
            href = link.get('href')

            result = urlsplit(href)

            scheme = result.scheme or self.scheme
            netloc = result.netloc or self.netloc
            path = result.path
            if scheme not in ("http", "https"):
                # Deal with non-HTTP urls
                continue

            if netloc != self.netloc:
                # Deal with external links
                continue

            if not path:
                continue

            tmpurl = url
            if "." not in url and not url.endswith("/"):
                tmpurl = url + "/"

            new_url = urljoin(tmpurl, path)

            if new_url not in self._origin_urls:
                #print url, "->", new_url
                self._origin_urls[new_url] = url
                self._pending_links.append(new_url)


if __name__ == "__main__":
    main()
