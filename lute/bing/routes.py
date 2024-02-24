"""
Getting and saving bing image search results.
"""

import os
import re
import urllib.request
from flask import Blueprint, request, Response, render_template, jsonify, current_app


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


def _get_dir_and_filename(langid, text):
    "Make a directory if needed, return [dir, filename]"
    datapath = current_app.config["DATAPATH"]
    image_dir = os.path.join(datapath, "userimages", langid)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    filename = re.sub(r"\s+", "_", text) + ".jpeg"
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

    # This is the format of legacy Lute v2 data.
    image_url = f"/userimages/{langid}/{filename}"
    return jsonify({"filename": image_url})


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

    # This is the format of legacy Lute v2 data.
    image_url = f"/userimages/{langid}/{filename}"
    return jsonify({"filename": image_url})
