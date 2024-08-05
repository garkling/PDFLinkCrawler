from scrapy.exceptions import DropItem


class PDFUniqueLinkPipeline:

    links = set()

    def process_item(self, item, _spider):
        link = item["link"]
        if link in self.links:
            raise DropItem

        self.links.add(link)
        return item
