import json
import logging
_logger = logging.getLogger(__name__)
import requests

def get_bulx_authintecation():
    url = 'https://bulxperformancetestidentityserver.azurewebsites.net/connect/token'

    aouth = requests.post(url=url, data={"grant_type": "client_credentials",
                                         "client_secret": "bulx_odoo_client_secret",
                                         "client_id": "bulx_odoo_client",
                                         "scope": "bulx_backend"})
    text_val = aouth.text
    res = json.loads(text_val)
    token_id = res['access_token']
    return token_id