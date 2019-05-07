from scrapy import cmdline
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    cmdline.execute("scrapy crawl restaurants".split())
