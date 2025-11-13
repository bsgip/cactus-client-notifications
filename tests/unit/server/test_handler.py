import pytest
from assertical.fake.generator import generate_class_instance

from cactus_client_notifications.server.handler import generate_public_uri, path_join
from cactus_client_notifications.server.settings import ServerSettings


@pytest.mark.parametrize(
    "parts, expected",
    [
        ([], ""),
        (["abc"], "abc"),
        (["abc", "/", "/", "", "/", "def"], "abc/def"),
        (["abc", "/", "/", "", "/", "def", "/", "/"], "abc/def/"),
        (["abc", "def"], "abc/def"),
        (["abc", "def"], "abc/def"),
        (["abc/", "def"], "abc/def"),
        (["abc", "/def"], "abc/def"),
        (["abc/", "/def"], "abc/def"),
        (["/abc/", "/def/"], "/abc/def/"),
        ([" /abc/ ", " /def/ ", "   ", " / "], "/abc/def/"),
        (["https://foo.com:123/", "/", "/def/", "", "efg", "hij/"], "https://foo.com:123/def/efg/hij/"),
    ],
)
def test_path_join(parts, expected):
    actual = path_join(*parts)
    assert isinstance(actual, str)
    assert expected == actual


@pytest.mark.parametrize(
    "public_uri, mount_point, id, expected",
    [
        ("https://foo.bar:123/", "/", "abc123", "https://foo.bar:123/webhook/abc123"),
        ("http://foo.bar.baz:456", "api", "DEF456", "http://foo.bar.baz:456/api/webhook/DEF456"),
    ],
)
def test_generate_public_uri(public_uri, mount_point, id, expected):
    actual = generate_public_uri(
        generate_class_instance(ServerSettings, public_server_url=public_uri, mount_point=mount_point), id
    )
    assert isinstance(actual, str)
    assert expected == actual
