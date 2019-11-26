# DATA SOURCING ---------------------------------------------------
# .. etl process script
# http data download setup (default certificates)..
# 1. python -m pip install certifi
# 2. in terminal: /Applications/Python\ 3.7/Install\ Certificates.command
import urllib.request
from crontab import CronTab

# major leagues ---------------------------------------------------
url_source = 'http://football-data.co.uk/mmz4281/1920/all-euro-data-2019-2020.xlsx'
url_store = 'src_data/'
file_nm = 'latest_results_ml.xlsx'
# store the file in the global-databases folder
urllib.request.urlretrieve(url_source, url_store + file_nm)

# niche leagues ---------------------------------------------------
url_source = 'https://www.football-data.co.uk/new/new_leagues_data.xlsx'
url_store = 'src_data/'
file_nm = 'latest_results_nl.xlsx'
# store the file in the global-databases folder
urllib.request.urlretrieve(url_source, url_store + file_nm)












