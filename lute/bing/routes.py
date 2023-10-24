from flask import Blueprint, request, render_template, jsonify
import os
import urllib.request
import re

bp = Blueprint('bing', __name__, url_prefix='/bing')

@bp.route('/search/<int:langid>/<string:text>/<string:searchstring>', methods=['GET'])
def bing_search(langid, text, searchstring):
    "Do an image search."

    # Searching for images slows acceptance tests.  If NO_BING_IMAGES
    # environment setting, don't do a search.
    if 'NO_BING_IMAGES' in os.environ:
        return render_template(
            'imagesearch/index.html',
            langid=langid, text=text, images=[])

    # dump("searching for " + text + " in " + language.getLgName())
    search = urllib.parse.quote(text)
    searchparams = searchstring.replace("###", search)
    url = "https://www.bing.com/images/search?" + searchparams
    content = urllib.request.urlopen(url).read().decode('utf-8')

    # Samples
    # <img class="mimg vimgld" ... data-src="https:// ...">
    # or
    # <img class="mimg rms_img" ... src="https://tse4.mm.bing ..." >
    
    pattern = r'(<img .*?>)'
    matches = re.findall(pattern, content, re.I)
    
    images = list(matches)

    is_search_img = lambda img: not ('src="/' in img) and ('rms_img' in img or 'vimgld' in img)
    images = list(filter(is_search_img, images))

    fix_data_src = lambda img: img.replace('data-src=', 'src=')
    images = list(map(fix_data_src, images))

    # Reduce image load count so we don't kill subpage loading.
    images = images[:25]

    build_struct = lambda image: {
        'html': image,
        'src': re.search(r'src="(.*?)"', image).group(1) if re.search(r'src="(.*?)"', image) else 'missing'
    }
    data = list(map(build_struct, images))

    return render_template('imagesearch/index.html', langid=langid, text=text, images=data)


def make_filename(text):
    return re.sub(r'\s+', '_', text) + '.jpeg'


@bp.route('/save', methods=['POST'])
def bing_save():
    src = request.form['src']
    text = request.form['text']
    langid = request.form['langid']

    publicdir = '/userimages/' + str(langid) + '/'
    realdir = os.path.join(os.path.dirname(__file__), '..', 'data', publicdir)
    if not os.path.exists(realdir):
        os.makedirs(realdir)
    filename = make_filename(text)
    with urllib.request.urlopen(src) as response, open(os.path.join(realdir, filename), 'wb') as out_file:
        out_file.write(response.read())

    return jsonify({'filename': publicdir + filename})
