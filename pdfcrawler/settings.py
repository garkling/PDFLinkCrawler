BOT_NAME = "pdfcrawler"

SPIDER_MODULES = ["pdfcrawler.spiders"]
NEWSPIDER_MODULE = "pdfcrawler.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.1
COOKIES_ENABLED = False

ITEM_PIPELINES = {
   "pdfcrawler.pipelines.PDFUniqueLinkPipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
DEFAULT_URL_SCHEME_ON_MISSING = "https://"
