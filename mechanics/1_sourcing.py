# DATA SOURCING ---------------------------------------------------
import urllib.request
from datetime import datetime
from fooStrat.processing import fp_cloud
# split into categories: historical, latest, fixtures

# Download the latest data ----------------------------------------

# football-data.co.uk ---------------------------------------------
url_source = ['https://www.football-data.co.uk/mmz4281/2021/all-euro-data-2020-2021.xlsx',
              'https://www.football-data.co.uk/new/new_leagues_data.xlsx',
              'https://www.football-data.co.uk/fixtures.xlsx',
              'https://www.football-data.co.uk/new_league_fixtures.xlsx']
file_nm = ['latest_results_major.xlsx',
           'latest_results_minor.xlsx',
           'latest_fixtures_major.xlsx',
           'latest_fixtures_minor.xlsx']

url_store = fp_cloud + 'src_data/'
for ob in range(len(url_source)):
    urllib.request.urlretrieve(url_source[ob], url_store + file_nm[ob])
    print(url_source[ob], file_nm[ob])


# last update stamp -----------------------------------------------
fl = url_store + 'data_updated.txt'
fo = open(fl, 'a+')
fo.write('\nData updated on ' + str(datetime.now()))
fo.close()











