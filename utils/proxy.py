"""代理配置：读取环境变量并供浏览器 / HTTP 客户端使用。"""

from __future__ import annotations

import os
from urllib.parse import unquote, urlparse


def get_proxy_server(*, use_proxy: bool = True) -> str | None:
	"""按平台配置读取 CHECKIN_PROXY_URL；use_proxy=False 时不返回代理地址。"""
	if not use_proxy:
		return None
	server = os.getenv('CHECKIN_PROXY_URL', '').strip()
	return server or None


def get_playwright_proxy(*, use_proxy: bool = True) -> dict[str, str] | None:
	server = get_proxy_server(use_proxy=use_proxy)
	if not server:
		return None
	parsed = urlparse(server)
	# 显式拆解 username 和 password 喂给 Playwright
	if parsed.username and parsed.password:
		port_part = f':{parsed.port}' if parsed.port is not None else ''
		clean_server = f'{parsed.scheme}://{parsed.hostname}{port_part}'
		return {
			'server': clean_server,
			'username': unquote(parsed.username),
			'password': unquote(parsed.password),
		}
	return {'server': server}
