import os
import argparse
import requests
import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--token', type=str, required=True, help='Zenodo Token.')
parser.add_argument('--deposit', type=str, required=True, help='Deposit ID.')
parser.add_argument('files', nargs='+', help='All files that should be uploaded.')
opt, unknown_opt = parser.parse_known_args()

# Connect and verify token
params = {'access_token': opt.token}

r = requests.get('https://zenodo.org/api/deposit/depositions', params=params)

if r.status_code != 200:
    print("Unable to connect or verify access token (Status code: %s)." % (r.status_code))
    exit

print("Connected to Zenodo REST API and token verified.")

# Get deposit links
headers = {"Content-Type": "application/json"}
r = requests.get('https://zenodo.org/api/deposit/depositions/%s' % (opt.deposit),
                   params=params,
                   json={},
                   # Headers are not necessary here since "requests" automatically
                   # adds "Content-Type: application/json", because we're using
                   # the "json=" keyword argument
                   # headers=headers,
                   headers=headers)

if r.status_code != 200:
    print("Unable to receive deposit metadata (Status code: %s)." % (r.status_code))
    exit

print("Metadata of the deposit downloaded.")

bucket_url = r.json()["links"]["bucket"]

# Upload files
for file in tqdm.tqdm(opt.files):
    path = file
    filename = os.path.basename(path)

    # The target URL is a combination of the bucket link with the desired filename
    # seperated by a slash.
    with open(path, "rb") as fp:
        r = requests.put("%s/%s" % (bucket_url, filename),
            params=params,
            data=fp,
        )

print("Please verify in WebUI if all files are online.")