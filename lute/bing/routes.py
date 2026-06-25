"""
Getting and saving bing image search results.
"""

import os
import datetime
import hashlib
import re
import urllib.request
import json
from flask import (
    Blueprint,
    request,
    Response,
    render_template,
    jsonify,
    current_app,
    url_for,
)


bp = Blueprint("bing", __name__, url_prefix="/bing")


@bp.route(
    "/search_page/<int:langid>/<string:text>/<string:searchstring>", methods=["GET"]
)
def bing_search_page(langid, text, searchstring):
    """
    Load initial empty search page, passing real URL for subsequent ajax call to get images.

    Sometimes Bing image searches block or fail, so providing the initial empty search page
    lets the user know work is in progress.  The user can therefore interact with the page
    immediately. The template for this route then makes an ajax call to the "bing_search()"
    method below which actually does the search.
    """

    # Create URL for bing_search and pass into template.
    search_url = url_for(
        "bing.bing_search", langid=langid, text=text, searchstring=searchstring
    )

    return render_template(
        "imagesearch/index.html", langid=langid, text=text, search_url=search_url
    )


@bp.route("/search/<int:langid>/<string:text>/<string:searchstring>", methods=["GET"])
def bing_search(langid, text, searchstring):
    "Do an image search."

    # pylint: disable=too-many-locals
    # Searching for images slows acceptance tests.  If NO_BING_IMAGES
    # environment setting, don't do a search.
    if "NO_BING_IMAGES" in os.environ:
        return render_template(
            "imagesearch/index.html", langid=langid, text=text, images=[]
        )

    search = urllib.parse.quote(text)
    params = searchstring.replace("[LUTE]", search)
    params = params.replace("###", search)  # TODO remove_old_###_placeholder: remove

    url = "https://www.bing.com/images/async?" + params + "&first=1&count=35&mmasync=1"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    content = ""
    error_msg = ""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as s:
            content = s.read().decode("utf-8")
    except urllib.error.URLError as e:
        content = ""
        error_msg = str(e.reason)
    except Exception as e:  # pylint: disable=broad-exception-caught
        content = ""
        error_msg = str(e)

    # Sample data returned by bing image search:
    # <img class="mimg vimgld" ... data-src="https:// ...">
    # or
    # <img class="mimg rms_img" ... src="https://tse4.mm.bing ..." >
    images = []
    for m_data in re.findall(r' m="({.*?})"', content):
        try:
            data = json.loads(m_data.replace("&quot;", '"'))
            murl = data.get("murl", "")
            if murl and murl.startswith("http"):
                images.append({"html": '<img src="' + murl + '">', "src": murl})
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    if not images:

        def is_search_img(img):
            if 'src="/' in img:
                return False
            normalized = img.replace("data-src=", "src=")
            return bool(re.search(r'src="https?://', normalized))

        def build_struct(image):
            src = "missing"
            normalized_source = image.replace("data-src=", "src=")
            m = re.search(r'src="(.*?)"', normalized_source)
            if m:
                src = m.group(1)
            return {"html": image, "src": src}

        raw_images = list(re.findall(r"(<img .*?>)", content, re.I))
        images = [build_struct(i) for i in raw_images if is_search_img(i)]

    # Reduce image load count so we don't kill subpage loading.
    # Also bing seems to throttle images if the count is higher (??).
    images = images[:25]

    ret = {
        "langid": langid,
        "text": text,
        "images": images,
        "error_message": error_msg,
    }
    return jsonify(ret)


def _get_dir_and_filename(langid, text):
    "Make a directory if needed, return [dir, filename]"
    datapath = current_app.config["DATAPATH"]
    image_dir = os.path.join(datapath, "userimages", langid)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S%f")[:-3]
    hash_part = hashlib.md5(text.encode()).hexdigest()[:8]
    filename = f"{timestamp}_{hash_part}.jpeg"
    return [image_dir, filename]


@bp.route("/save", methods=["POST"])
def bing_save():
    """
    Save the posted image data to DATAPATH/userimages,
    returning the filename.
    """
    src = request.form["src"]
    text = request.form["text"]
    langid = request.form["langid"]

    imgdir, filename = _get_dir_and_filename(langid, text)
    destfile = os.path.join(imgdir, filename)
    with urllib.request.urlopen(src) as response, open(destfile, "wb") as out_file:
        out_file.write(response.read())

    ret = {
        "url": f"/userimages/{langid}/{filename}",
        "filename": filename,
    }
    return jsonify(ret)


@bp.route("/manual_image_post", methods=["POST"])
def manual_image_post():
    """
    For manual posts of images (not bing image clicks).
    Save the posted image data to DATAPATH/userimages,
    returning the filename.
    """
    text = request.form["text"]
    langid = request.form["langid"]

    if "manual_image_file" not in request.files:
        return Response("No file part in request", status=400)

    f = request.files["manual_image_file"]
    if f.filename == "":
        return Response("No selected file", status=400)

    imgdir, filename = _get_dir_and_filename(langid, text)
    destfile = os.path.join(imgdir, filename)
    f.save(destfile)

    ret = {
        "url": f"/userimages/{langid}/{filename}",
        "filename": filename,
    }
    return jsonify(ret)
