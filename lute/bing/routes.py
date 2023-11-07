"""
Getting and saving bing image search results.
"""

import os
import re
import urllib.request
from flask import Blueprint, request, render_template, jsonify, current_app


bp = Blueprint("bing", __name__, url_prefix="/bing")


@bp.route("/search/<int:langid>/<string:text>/<string:searchstring>", methods=["GET"])
def bing_search(langid, text, searchstring):
    "Do an image search."

    # Searching for images slows acceptance tests.  If NO_BING_IMAGES
    # environment setting, don't do a search.
    if "NO_BING_IMAGES" in os.environ:
        return render_template(
            "imagesearch/index.html", langid=langid, text=text, images=[]
        )

    # dump("searching for " + text + " in " + language.getLgName())
    search = urllib.parse.quote(text)
    searchparams = searchstring.replace("###", search)
    url = "https://www.bing.com/images/search?" + searchparams
    content = ""
    with urllib.request.urlopen(url) as s:
        content = s.read().decode("utf-8")

    # Samples
    # <img class="mimg vimgld" ... data-src="https:// ...">
    # or
    # <img class="mimg rms_img" ... src="https://tse4.mm.bing ..." >

    pattern = r"(<img .*?>)"
    matches = re.findall(pattern, content, re.I)

    images = list(matches)

    def is_search_img(img):
        return not ('src="/' in img) and ("rms_img" in img or "vimgld" in img)

    def fix_data_src(img):
        return img.replace("data-src=", "src=")

    images = [fix_data_src(i) for i in images if is_search_img(i)]

    # Reduce image load count so we don't kill subpage loading.
    images = images[:25]

    def build_struct(image):
        src = "missing"
        m = re.search(r'src="(.*?)"', image)
        if m:
            src = m.group(1)
        return {"html": image, "src": src}

    data = [build_struct(i) for i in images]

    return render_template(
        "imagesearch/index.html", langid=langid, text=text, images=data
    )


def make_filename(text):
    return re.sub(r"\s+", "_", text) + ".jpeg"


@bp.route("/save", methods=["POST"])
def bing_save():
    """
    Save the posted image data to DATAPATH/userimages,
    returning the filename.
    """
    src = request.form["src"]
    text = request.form["text"]
    langid = request.form["langid"]

    datapath = current_app.config["DATAPATH"]
    imgdir = os.path.join(datapath, "userimages", langid)
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)
    filename = make_filename(text)
    destfile = os.path.join(imgdir, filename)
    with urllib.request.urlopen(src) as response, open(destfile, "wb") as out_file:
        out_file.write(response.read())

    # This is the format of legacy Lute v2 data.
    image_url = f"/userimages/{langid}/{filename}"
    return jsonify({"filename": image_url})
