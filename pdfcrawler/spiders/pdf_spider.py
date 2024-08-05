import json
import logging
from typing import Any
from urllib.parse import urlparse
from distutils.util import strtobool

import scrapy
import tldextract
from scrapy.http import Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS

from ..settings import DEFAULT_URL_SCHEME_ON_MISSING

IGNORED_EXTENSIONS = {*IGNORED_EXTENSIONS, "pkg"}


logger = logging.getLogger("scrapy.pdfs")


class PDFLinkSpider(scrapy.Spider):

    EXTENSION = "pdf"
    MIMETYPE = "application/pdf"

    name = 'pdfs'

    def __init__(self, start_urls: str, all_subdomains=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_urls = self._prep_start_urls(start_urls)
        logger.info(f"Initialized the start URLs - {self.start_urls}")
        self.allowed_domains = self._prep_allowed_domains(all_subdomains)
        logger.info(f"Configured the allowed domains - {self.allowed_domains}")

        self.le = LinkExtractor(
            allow_domains=self.allowed_domains,
            deny_extensions={self.EXTENSION}.symmetric_difference(IGNORED_EXTENSIONS)   # excludes "pdf"
        )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        script_links = set()
        script_tag = response.css("script[type='application/json']::text").extract()

        # search in the <script> tags because of the dynamic content loading
        for pdf_links, other_links in self.parse_json(script_tag):
            script_links = {*script_links, *other_links}
            for link in pdf_links:
                yield dict(link=response.urljoin(link))

        page_links = {
            *self.le.extract_links(response),
            *(Link(response.urljoin(sl)) for sl in script_links)
        }

        for link in page_links:
            link: Link
            url = link.url
            if url.endswith('.' + self.EXTENSION):
                logger.info(f"Found the URL with the appropriate extension - {url}")
                yield dict(link=url)
            else:
                # kinda a light request just to check a type without downloading the content
                yield response.follow(url, method="HEAD", callback=self.parse_item)

    def parse_json(self, script_bodies):
        for raw in script_bodies:
            try:
                data = json.loads(raw)
                yield self.extract_pdf_links_from_json(data)
            except json.decoder.JSONDecodeError:
                logger.error(f"Invalid JSON in <script> tag - {raw[:30]}...{raw[30:]}")

    def parse_item(self, response: Response) -> Any:
        url = response.url
        # match by the response content type if the extension is missing
        if self.MIMETYPE.encode() in response.headers["Content-Type"]:
            logger.info(f"Found the URL with the appropriate mimetype - {url}")
            yield dict(link=url)
        else:
            # a complete GET request after the HEAD one
            yield response.follow(url, callback=self.parse, dont_filter=True)

    def extract_pdf_links_from_json(self, data: dict, pdf_links=None, other_links=None):
        """
        Recursively extracts all links from all the <script type="application/json"> JSON bodies on the page
        """
        if pdf_links is None: pdf_links = set()
        if other_links is None: other_links = set()

        if isinstance(data, dict):
            for key, value in data.items():
                self.extract_pdf_links_from_json(value, pdf_links, other_links)
        elif isinstance(data, list):
            for item in data:
                self.extract_pdf_links_from_json(item, pdf_links, other_links)
        elif isinstance(data, str):
            _, netloc, path, *_ = urlparse(data)
            if netloc and path:
                if path.endswith('.' + self.EXTENSION):
                    pdf_links.add(data)
                else:
                    other_links.add(data)

        return pdf_links, other_links

    @staticmethod
    def _prep_start_urls(urls: str) -> list:
        """
        Splits given URL string into a list of raw URLs.
        Checks if the given start URLs contain a scheme otherwise strips the leading slashes and prepends the default scheme.
        Returns a list without duplicates
        """
        start_urls = map(
            lambda u: DEFAULT_URL_SCHEME_ON_MISSING + u.lstrip('/') if not urlparse(u).scheme else u,
            urls.split(',')
        )
        return list(set(start_urls))

    def _prep_allowed_domains(self, all_subdomains=False) -> list:
        """
        Fetches domains from the start URLs and returns a list without duplicates.
        If all_subdomains is True - gets a domain.suffix form, otherwise gets a subdomain.domain.suffix form
        """
        all_subdomains = strtobool(all_subdomains) if isinstance(all_subdomains, str) else all_subdomains
        allowed = map(
            lambda u: tldextract.extract(urlparse(u).netloc).registered_domain,
            self.start_urls
        ) if all_subdomains else map(
            lambda u: urlparse(u).netloc, self.start_urls
        )
        return list(set(allowed))
