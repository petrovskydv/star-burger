import subprocess

import requests
from environs import Env

env = Env()
env.read_env()
# fetch last committed revision in the locally-checked out branch
git_process = subprocess.run(['git', 'log', '-n', '1', '--pretty=format:%H'], capture_output=True, check=True)
revision = git_process.stdout.decode()

response = requests.post('https://api.rollbar.com/api/1/deploy/', json={
    'environment': env('ROLLBAR_ENVIRONMENT', 'development'),
    'revision': revision
}, headers={
    'X-Rollbar-Access-Token': env('ROLLBAR_TOKEN'),
}, timeout=3)

response.raise_for_status()
print(response.json())
