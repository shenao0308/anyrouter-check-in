from utils.proxy import get_playwright_proxy, get_proxy_server


def test_get_proxy_server_when_disabled(monkeypatch):
	monkeypatch.setenv('CHECKIN_PROXY_URL', 'http://127.0.0.1:7890')
	assert get_proxy_server(use_proxy=False) is None


def test_get_proxy_server_when_not_set(monkeypatch):
	monkeypatch.delenv('CHECKIN_PROXY_URL', raising=False)
	assert get_proxy_server(use_proxy=True) is None


def test_playwright_proxy_without_auth(monkeypatch):
	monkeypatch.setenv('CHECKIN_PROXY_URL', 'http://127.0.0.1:7890')
	proxy = get_playwright_proxy(use_proxy=True)
	assert proxy == {'server': 'http://127.0.0.1:7890'}


def test_playwright_proxy_with_auth_and_port(monkeypatch):
	monkeypatch.setenv('CHECKIN_PROXY_URL', 'http://user123:pass456@proxy.example.com:8080')
	proxy = get_playwright_proxy(use_proxy=True)
	assert proxy == {
		'server': 'http://proxy.example.com:8080',
		'username': 'user123',
		'password': 'pass456',
	}


def test_playwright_proxy_with_auth_without_explicit_port(monkeypatch):
	monkeypatch.setenv('CHECKIN_PROXY_URL', 'http://user123:pass456@proxy.example.com')
	proxy = get_playwright_proxy(use_proxy=True)
	assert proxy is not None
	assert proxy['server'] == 'http://proxy.example.com'
	assert proxy['username'] == 'user123'
	assert proxy['password'] == 'pass456'


def test_playwright_proxy_with_url_encoded_credentials(monkeypatch):
	monkeypatch.setenv('CHECKIN_PROXY_URL', 'http://user%40work.com:p%40ss%23word@proxy.example.com:8080')
	proxy = get_playwright_proxy(use_proxy=True)
	assert proxy is not None
	assert proxy['server'] == 'http://proxy.example.com:8080'
	assert proxy['username'] == 'user@work.com'
	assert proxy['password'] == 'p@ss#word'
