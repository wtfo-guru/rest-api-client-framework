import hashlib
from http import HTTPStatus

from pyfakefs.fake_filesystem import FakeFilesystem
from requests import Response

from api_client.response import RestResponse


def assert_file_hash(file_path: str, match: str):
    with open(file_path, "rb") as fp:
        image = fp.read()

    md5 = hashlib.md5(usedforsecurity=False)
    md5.update(image)
    md5_hash = md5.hexdigest()

    assert md5_hash == match


def test_parse_response(response: Response):
    resp = RestResponse(response)
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers == {
        "content-type": "application/json",
        "accept": "application/gzip",
    }
    assert resp.is_json()
    assert resp.data() == {"foo": "bar"}


def test_save_json_in_file(response: Response, fs: FakeFilesystem):
    fs.create_dir("/testing")
    resp = RestResponse(response)
    assert resp.is_json()
    assert resp.save("/testing/test.json")
    assert_file_hash("/testing/test.json", "94232c5b8fc9272f6f73a1e36eb68fcf")


def test_image_as_response(response_image: Response):
    resp = RestResponse(response_image)
    assert resp.status_code == HTTPStatus.OK
    assert resp.headers == {
        "content-type": "image/png",
    }
    assert resp.is_json() is False
    assert resp.save("/tmp/image.png") == "/tmp/image.png"
    assert_file_hash("/tmp/image.png", "d16fbdccd830021d48d0a7498b0c4456")
