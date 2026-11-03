"""render.mjs 静态服务器：只监听回环地址、拒绝目录穿越（用原始套接字发请求，避免客户端先规整路径）。"""
import json
import subprocess

import pytest

from conftest import ROOT
pytestmark = pytest.mark.env   # 需要 node_modules（playwright-core）

SCRIPT = """import { serve } from './render.mjs';
import net from 'node:net';
const srv = await serve();
const { address, port } = srv.address();
const raw = path => new Promise(res => {
  const s = net.connect(port, '127.0.0.1', () => s.write(`GET ${path} HTTP/1.0\\r\\n\\r\\n`));
  let d = ''; s.on('data', c => d += c); s.on('close', () => res(+d.split(' ')[1]));
});
const out = { address };
for (const p of ['/package.json', '/../../../../../../etc/hosts', '/..%2f..%2f..%2f..%2f..%2f..%2fetc/hosts', '/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/hosts', '/src/%E0%A4%A'])
  out[p] = await raw(p);
srv.close();
console.log(JSON.stringify(out));
"""


def test_static_server_loopback_and_no_traversal():
    r = subprocess.run(['node', '--input-type=module', '-e', SCRIPT], cwd=ROOT, capture_output=True, text=True, check=True)
    out = json.loads(r.stdout)
    assert out.pop('address') == '127.0.0.1'
    assert out.pop('/package.json') == 200
    assert out and all(code in (400, 404) for code in out.values()), out
