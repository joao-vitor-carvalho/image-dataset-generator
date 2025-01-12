
from flickrapi import FlickrAPI
import urllib
from PIL import Image
import requests
import os
from dotenv.main import load_dotenv
import math
from query_reader import Queries
import threading


load_dotenv()
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
MODEL_NAME = os.environ['MODEL_NAME']
DATASET_SIZE = int(os.environ['DATASET_SIZE'])
DATASET_PATH = '../../dataset_flickr/'

flickr = FlickrAPI(
    API_KEY,
    API_SECRET,
    format='parsed-json'
)


MAX_PER_PAGE = 500  # max images per flickr request


class FlickrScript:
    # class that manages the flickr api queries
    def __init__(self,  extras='description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'):
        self.queries = Queries()  # queries list
        self.extras = extras     # All the extra data that I want to have
        self.threads = []    # threds list

    def download(self):
        for query in self.queries.getQueries():
            self.threads.append(threading.Thread(
                target=self.downloadPhotos, args=(query,)))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

        # for query in self.queries.getQueries():

        #     total_downloaded = 0
        #     current_page = 1
        #     final_page = 1
        #     self.unwanted_tags = query['unwanted_tags']
        #     while (self.total_downloaded < DATASET_SIZE) and (current_page <= final_page):

        #         photos = flickr.photos.search(
        #             text=query['name'],  # Search term
        #             per_page=MAX_PER_PAGE,  # Number of results per page #max = 500
        #             extras=self.extras,
        #             page=current_page,
        #             privacy_filter=1,  # public photos
        #             safe_search=1  # is safe
        #         )
        #         self.total_results = photos['photos']['total']
        #         photos = photos['photos']['photo']
        #         final_page = math.ceil(self.total_results / MAX_PER_PAGE)
        #         self.downloadPage(photos, query, total_downloaded=total_downloaded)
        #         current_page += 1

    def downloadPhotos(self, query):
        total_downloaded = 0
        current_page = 1
        final_page = 1
        self.unwanted_tags = query['unwanted_tags']
        while (total_downloaded < DATASET_SIZE) and (current_page <= final_page):

            photos = flickr.photos.search(
                text=query['name'],  # Search term
                per_page=MAX_PER_PAGE,  # Number of results per page #max = 500
                extras=self.extras,
                page=current_page,
                privacy_filter=1,  # public photos
                safe_search=1  # is safe
            )
            total_results = photos['photos']['total']
            photos = photos['photos']['photo']
            final_page = math.ceil(total_results / MAX_PER_PAGE)
            self.downloadPage(photos, query, total_downloaded)
            current_page += 1

    def downloadPage(self, photos, query, total_downloaded):
        # Download all photos

        if not os.path.exists(DATASET_PATH + query['name']):
            os.makedirs(DATASET_PATH + query['name'])
        for photo in photos:
            if ('url_c' in photo) and not self.checkUnwantedTags(photo) and (total_downloaded < DATASET_SIZE):
                print('Downloading image No: ', total_downloaded, ' Dataset Size: ',  DATASET_SIZE,
                      '\n Query: ', query['name'], 'Tags: ', photo['tags'])
                url = photo['url_c']
                # check if file already exists:
                if (photo['id'] + '.jpg') not in os.listdir(DATASET_PATH + query['name'] + '/'):
                    urllib.request.urlretrieve(
                        url, DATASET_PATH + query['name'] + '/' + photo['id'] + ".jpg")
                    total_downloaded += 1

    def checkUnwantedTags(self, photo):
        # checks if photo has any of the unwanted tags in its metadata
        # return true if it has unwanted tags
        for tag in self.unwanted_tags:
            if tag in photo['tags']:
                return True
        return False


def main():

    flickr_script = FlickrScript()
    flickr_script.download()


if __name__ == "__main__":
    main()
