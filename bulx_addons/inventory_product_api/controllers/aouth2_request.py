import json
import logging
_logger = logging.getLogger(__name__)
import requests

url = 'https://bulxperformancetestidentityserver.azurewebsites.net/connect/token'

aouth = requests.post(url=url, data={"grant_type": "client_credentials",
                                     "client_secret": "bulx_odoo_client_secret",
                                     "client_id": "bulx_odoo_client",
                                     "scope": "bulx_backend"})
text_val = aouth.text
res = json.loads(text_val)
token_id = res['access_token']
print(res['access_token'])
header_token = 'access_token {}'.format(token_id)
print(header_token)
try:
    request = requests.get('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Brands', params=None,headers={'Authorization': 'Bearer %s' % token_id}, )
    print(request)
    request.raise_for_status()
    # return request.json()
except requests.HTTPError as e:
    _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                  e.response.status_code, e.response.reason, e.response.content)

res = requests.get('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Brands',
                   headers={'Authorization': 'Bearer %s' % token_id})
print(res, res.content)
# cat = {}
# res = requests.post('https://bulxidentityserver.azurewebsites.net/api/v1/Catalog/Categories',data=cat, headers={'Authorization': 'access_token {}'.format(token_id)})
print(res.text)
