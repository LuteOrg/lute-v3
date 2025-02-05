/* Posting to Anki via AnkiConnect. */

const LuteAnki = (function() {

  /* copied verbatim from
   * https://foosoft.net/projects/anki-connect/index.html#miscellaneous-actions */
  function _invoke(postdict) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('error', () => reject('failed to issue request'));
        xhr.addEventListener('load', () => {
            try {
                const response = JSON.parse(xhr.responseText);
                if (Object.getOwnPropertyNames(response).length != 2) {
                    throw 'response has an unexpected number of fields';
                }
                if (!response.hasOwnProperty('error')) {
                    throw 'response is missing required error field';
                }
                if (!response.hasOwnProperty('result')) {
                    throw 'response is missing required result field';
                }
                if (response.error) {
                    throw response.error;
                }
                resolve(response.result);
            } catch (e) {
                reject(e);
            }
        });

        xhr.open('POST', 'http://127.0.0.1:8765');
        xhr.send(JSON.stringify(postdict));
    });
  }

  /**
   * Queries anki and gets data.
   */
  async function get_anki_specs(anki_connect_url) {
    let p = {
      "action": "multi",
      "version": 6,
      "params": {
        "actions": [
          { "action": "deckNames" },
          { "action": "modelNames" },
        ]
      }
    }
    result = await _invoke(p);
    // console.log(`got: ${JSON.stringify(result, null, 2)}`)

    const deck_names = result[0];
    const note_types = result[1];

    const getfieldnames_actions = note_types.map(nt => ({
      "action": "modelFieldNames",
      "params": {
        "modelName": nt
      }
    }));
    // console.log(JSON.stringify(getfieldnames_actions, null, 2));

    p = {
      "action": "multi",
      "version": 6,
      "params": { "actions": getfieldnames_actions }
    };
    result = await _invoke(p);
    // console.log(`got: ${JSON.stringify(result, null, 2)}`)
    const note_type_fields = {};
    for (let i = 0; i < note_types.length; i++) {
      note_type_fields[note_types[i]] = result[i];
    }
    // console.log(`got: ${JSON.stringify(note_type_fields, null, 2)}`)

    const ret = {
      deck_names: deck_names,
      note_types: note_type_fields,
    };
    // console.log(`got: ${JSON.stringify(ret, null, 2)}`)
    return ret;
  }


  // Exported functions.
  return {
    get_anki_specs: get_anki_specs,
  };


})();
