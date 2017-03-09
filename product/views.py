import os
import csv
import datetime
import mimetypes
import scrapy

from django.shortcuts import render
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.http import HttpResponse

from scrapy.crawler import CrawlerProcess

from costco_scraper.costco_scraper.spiders.costco_spider import CostcoSpider
from .models import *

def export_products(request):
    if request.method == "POST":
        product_ids = request.POST.get('ids').split(',')
        result_csv_fields = request.POST.getlist('props[]')

        path = datetime.datetime.now().strftime("/tmp/.costco_products_%Y_%m_%d_%H_%M_%S.csv")
        result = open(path, 'w')
        result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
        result_csv.writeheader()

        queryset = Product.objects.filter(id__in=product_ids)

        for product in queryset:
            product_ = model_to_dict(product, fields=result_csv_fields)
            for key, val in product_.items():
                if type(val) not in (float, int) and val:
                    product_[key] = val.encode('utf-8')

            try:
                result_csv.writerow(product_)
            except Exception, e:
                print product_
                raise e

        result.close()

        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) # not FileField instance
        response['Content-Disposition'] = 'attachment; filename=%s/' % smart_str( os.path.basename( path ) ) # same here        
        return response

def run_scrapy(request):
    process = CrawlerProcess()

    process.crawl(MySpider)
    process.start()
    return HttpResponse('Scraper is completed successfully!')
