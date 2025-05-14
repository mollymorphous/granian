import httpx
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('server_static_files', ['asgi', 'rsgi', 'wsgi'], indirect=True)
@pytest.mark.parametrize('runtime_mode', ['mt', 'st'])
async def test_static_files(server_static_files, runtime_mode):
    async with server_static_files(runtime_mode) as port:
        res = httpx.get(f'http://localhost:{port}/static/media.png')

    assert res.status_code == 200
    assert res.headers.get('content-type') == 'image/png'
    assert res.headers.get('cache-control')


@pytest.mark.asyncio
@pytest.mark.parametrize('server_static_files', ['asgi', 'rsgi', 'wsgi'], indirect=True)
@pytest.mark.parametrize('runtime_mode', ['mt', 'st'])
async def test_static_files_notfound(server_static_files, runtime_mode):
    async with server_static_files(runtime_mode) as port:
        res = httpx.get(f'http://localhost:{port}/static/missing.png')

    assert res.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize('server_static_files', ['asgi', 'rsgi', 'wsgi'], indirect=True)
@pytest.mark.parametrize('runtime_mode', ['mt', 'st'])
async def test_static_files_outsidemount(monkeypatch, server_static_files, runtime_mode):
    monkeypatch.setattr(httpx._urlparse, 'normalize_path', lambda v: v)

    async with server_static_files(runtime_mode) as port:
        res = httpx.get(f'http://localhost:{port}/static/../conftest.py')

    assert res.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize('server_static_files', ['asgi', 'rsgi', 'wsgi'], indirect=True)
@pytest.mark.parametrize('runtime_mode', ['mt', 'st'])
async def test_static_files_approute(server_static_files, runtime_mode):
    async with server_static_files(runtime_mode) as port:
        res = httpx.get(f'http://localhost:{port}/info')

    assert res.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize('server_static_files', ['asgi', 'rsgi', 'wsgi'], indirect=True)
@pytest.mark.parametrize('runtime_mode', ['mt', 'st'])
@pytest.mark.parametrize(
    'encoding',
    [
        ('identity', None, 140),
        ('gzip', 'gzip', 110),
        ('gzip, zstd', 'zst', 91),
        ('gzip, zstd, br', 'br', 70),
    ],
)
async def test_static_files_precompressed(server_static_files, runtime_mode, encoding):
    accept_encoding, content_encoding, body_length = encoding

    async with server_static_files(runtime_mode) as port:
        res = httpx.get(
            f'http://localhost:{port}/static/precompressed/script.js',
            headers={'accept-encoding': accept_encoding},
        )

    assert res.status_code == 200
    assert res.headers.get('content-type') == 'text/javascript'
    assert res.headers.get('content-encoding') == content_encoding
    assert len(await res.aread()) == body_length
