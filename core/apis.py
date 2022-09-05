import requests

url = "https://megabyte.com.ng/api/v2/datashare/?api_key={{api_key}}&product_name=data_share_1gb&phone=08012345678"

payload = ""
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

# # # # # # # # # # # # # #

import requests

url = "https://megabyte.com.ng/api/v2/datashare/?api_key={{api_key}}&product_name=data_share_1gb&phone=08012345678"

payload = ""
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)