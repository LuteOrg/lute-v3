/* Posting to Anki via AnkiConnect. */

const LuteAnki = (function() {

  /* initial draft copied verbatim from
   * https://foosoft.net/projects/anki-connect/index.html#miscellaneous-actions
   *
   * then converted to jquery, easier.
   */
  async function _invoke(postdict) {
    try {
      const response = await $.ajax({
        url: 'http://127.0.0.1:8765',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(postdict),
        dataType: 'json'
      });

      if (response.error) {
        throw new Error(response.error);
      }
    
      return response.result;
    } catch (error) {
      console.error("AnkiConnect error:", error.message);
      return null;
    }
  }

  /**
   * Queries anki and gets data.
   */
  async function _get_anki_specs(anki_connect_url) {
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

  async function get_anki_specs() {
    return _get_anki_specs()
      .then(result => {
        // console.log("result:", result);
        return result;
      })
      .catch(error => {
        console.log("Error getting specs");
        return null;
      });
  }

  async function get_post_data(word_ids) {
    // console.log("getting post data");

    const anki_specs = await get_anki_specs();
    // console.log("got specs?", anki_specs);

    if (!anki_specs) {
      console.log("Anki not running, or can't connect?");
      return null;
    }

    const { deck_names, note_types } = anki_specs;
    const postdata = {
      term_ids: word_ids,
      deck_names: deck_names,
      note_types: note_types,
    };

    try {
      const results = await $.ajax({
        url: "/ankiexport/get_card_post_data",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(postdata),
        dataType: "json"
      });

      if (results.error) {
        console.error("error:", results.error);
        return null;
      }

      return results;
    }
    catch (jqXHR) {
      console.error("AJAX request failed:", jqXHR.responseText || jqXHR.statusText);
      return null;
    }
  }

  // Exported functions.
  return {
    get_anki_specs: get_anki_specs,
    get_post_data: get_post_data,
  };
})();
