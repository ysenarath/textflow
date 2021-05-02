import json
import requests
from bs4 import BeautifulSoup


class TextFlowClient:
    def __init__(self, host, port=None, **kwargs):
        self.session = requests.session()
        self.host = host[:-1] if host[-1] == '/' else host
        self.port = port
        if ('username' in kwargs) and ('password' in kwargs):
            username, password = kwargs['username'], kwargs['password']
            self._login(username, password)

    def _url_of(self, path, **kwargs):
        if (self.port is None) or (self.port == ''):
            url = '{}{}'.format(self.host, path.format(**kwargs))
        else:
            url = '{}:{}{}'.format(self.host, self.port, path.format(**kwargs))
        return url

    def _login(self, username, password):
        url = self._url_of('/login')
        login_data = dict(username=username, password=password, csrf_token=self.csrf_token, next='/')
        self.session.post(url, data=login_data)

    @property
    def csrf_token(self):
        url = self._url_of('/login')
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf_token = soup.input.get("value")
        return csrf_token

    def get_status(self, project_id):
        url = self._url_of('/api/projects/{project_id}/status', project_id=project_id)
        payload = self.session.get(url).text
        return json.loads(payload)

    def get_dataset(self, project_id):
        kwargs = dict(project_id=project_id, validator='sys.majority')
        url = self._url_of('/api/projects/{project_id}/datasets/download?validator={validator}', **kwargs)
        payload = self.session.get(url).text
        return json.loads(payload)


def main():
    auth = dict(username='admin', password='admin@123')
    client = TextFlowClient('http://127.0.0.1/', port=5000, **auth)
    print(client.get_dataset(2))


if __name__ == '__main__':
    main()
