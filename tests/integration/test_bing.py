"""
Integration tests for Bing image search.
"""

from unittest.mock import patch, MagicMock
import urllib.error
import urllib.request


def test_bing_search_success_json_parsing(client):
    """
    Test successful search parsing when JSON data is present.
    """
    mock_response = MagicMock()
    html_content = """
    <html>
    <body>
        <div class="imgpt" m="{&quot;murl&quot;:&quot;https://example.com/image1.jpg&quot;}"></div>
        <div class="imgpt" m="{&quot;murl&quot;:&quot;https://example.com/image2.jpg&quot;}"></div>
    </body>
    </html>
    """
    mock_response.read.return_value = html_content.encode("utf-8")

    with patch("urllib.request.urlopen") as mock_urlopen, patch(
        "urllib.request.Request"
    ) as mock_request_cls:
        mock_urlopen.return_value.__enter__.return_value = mock_response

        resp = client.get("/bing/search/1/gato/q%3D%5BLUTE%5D")

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["langid"] == 1
        assert data["text"] == "gato"
        assert len(data["images"]) == 2
        assert data["images"][0]["src"] == "https://example.com/image1.jpg"
        assert data["images"][0]["html"] == '<img src="https://example.com/image1.jpg">'
        assert data["images"][1]["src"] == "https://example.com/image2.jpg"
        assert data["images"][1]["html"] == '<img src="https://example.com/image2.jpg">'

        mock_request_cls.assert_called_once()
        args, kwargs = mock_request_cls.call_args
        called_url = args[0]
        called_headers = kwargs.get("headers", {})

        assert "images/async" in called_url
        assert "q=gato" in called_url
        assert "User-Agent" in called_headers
        assert "Chrome/120.0.0.0" in called_headers["User-Agent"]


def test_bing_search_success_img_fallback(client):
    """
    Test successful search parsing when JSON data is not present, falling back to <img> tag parsing.
    """
    mock_response = MagicMock()
    html_content = """
    <html>
    <body>
        <img class="someclass" src="https://example.com/fallback1.jpg" />
        <img class="someclass" data-src="https://example.com/fallback2.jpg" />
    </body>
    </html>
    """
    mock_response.read.return_value = html_content.encode("utf-8")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_response

        resp = client.get("/bing/search/1/gato/q%3D%5BLUTE%5D")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["images"]) == 2
        assert data["images"][0]["src"] == "https://example.com/fallback1.jpg"
        assert data["images"][1]["src"] == "https://example.com/fallback2.jpg"


def test_bing_search_url_error(client):
    """
    Test search handles URLError.
    """
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Connection timed out")

        resp = client.get("/bing/search/1/gato/q%3D%5BLUTE%5D")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["images"] == []
        assert "Connection timed out" in data["error_message"]
