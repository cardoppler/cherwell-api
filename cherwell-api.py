import sys
import requests
import json

# Parameters
host = 'https://something.cherwellondemand.com/CherwellAPI'
user = 'some_user'
password = 'some_password'
client_id = 'some_client_id'
grant_type = 'password'
auth_mode='Internal'
busobid = 'somebusiness_id' # This corresponds to "Config - Server", This value might be different when pointing to the Prod API instead of Dev.

# Token request. A token is valid for 20 minutes after it has been requested. This python script does not care about that and requests a new token every time the script is run; this works fine and doesn't cause issues if the script is not run very often. (Improvement: compare the ".expires" datetime value in the returned response against the request time to evaluate whether to use an existing non-expired token or request a new one)
def get_token():
    data = "grant_type={0}&client_id={1}&username={2}&password={3}".format(grant_type, client_id, user, password)
    url = "{host}/token?auth_mode={auth_mode}".format(host=host, auth_mode=auth_mode)
    response = requests.post(url, data=data).json() # First API call: retrieves a new access token
    token = response.get('access_token')
    return token

# Helper function that creates a the correct HTTP headers given an access token. 
def create_headers_dict(access_token):
    headers = {"Authorization": "Bearer {}".format(access_token),
               "Content-type": "application/json",
               "Accept": "application/json"}
    return headers

# Get info. This is what downloads the info from Cherwell given the hostname
def get_info(publicid):
    url = '{0}/api/V1/getbusinessobject/busobid/{1}/publicid/{2}'.format(host, busobid, publicid)
    token = get_token()
    headers = create_headers_dict(token)
    response = requests.get(url, headers=headers) # Second API call: downloads host info from Cherwell
    response_dict = json.loads(response.content)
    if response.status_code != 200: # Exception
        print response_dict['errorCode']
        sys.exit()
    else: # 200 OK
        return (
                    response_dict['fields'][0]['value'],     # RecID
                    response_dict['fields'][6]['value'],     # LastModifiedDateTime
                    response_dict['fields'][20]['value'],    # IPAddress
                    response_dict['fields'][27]['value'],    # HostName
                    response_dict['fields'][46]['value'],    # CPUType
                    response_dict['fields'][47]['value'],    # CPUSpeed
                    response_dict['fields'][50]['value']     # PhysicalMemory
                )
        

# The script starts here:
# Check if a hostname is provided as input. If nothing is provided, then exit.
if len(sys.argv) != 2:
    print("Usage:       python cherwell-api.py hostname")
    sys.exit()
results = get_info(sys.argv[1])
print "|".join(results)
