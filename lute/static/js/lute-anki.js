/* Posting to Anki via AnkiConnect. */

const LuteAnki = (function() {

  /* initial draft copied verbatim from
   * https://foosoft.net/projects/anki-connect/index.html#miscellaneous-actions
   *
   * then converted to jquery, easier.
   */
  async function _invoke(anki_connect_url, postdict) {
    try {
      const response = await $.ajax({
        url: anki_connect_url,
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
      const lute_origin = window.location.origin;
      const msg = `Unable to connect to AnkiConnect at\n${anki_connect_url}.\n\n`
            + `Ensure Anki is running and AnkiConnect is installed,\n`
            + `and "${lute_origin}" (your Lute url) is in AnkiConnect's webCorsOriginList in its config.\n`
            + `(Remember to restart Anki if you change the AnkiConnect config.)`
      ;
      throw new Error(msg);
    }
  }

  /**
   * Get info about deck names and note types.
   * {
   *   deck_names: [ a, ... ],
   *   note_types: { n1: [ f1, f2 ], ...
   * }
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
    result = await _invoke(anki_connect_url, p);

    const deck_names = result[0];
    const note_types = result[1];

    const getfieldnames_actions = note_types.map(nt => ({
      "action": "modelFieldNames",
      "params": {
        "modelName": nt
      }
    }));

    p = {
      "action": "multi",
      "version": 6,
      "params": { "actions": getfieldnames_actions }
    };
    result = await _invoke(anki_connect_url, p);

    const note_type_fields = {};
    for (let i = 0; i < note_types.length; i++) {
      note_type_fields[note_types[i]] = result[i];
    }

    return {
      deck_names: deck_names,
      note_types: note_type_fields,
    };
  }

  /**
   * Returns a dict of ids to export name to AnkiConnect post data, eg:
   *
   * {
   *   42: {
   *     "export_1": post_1_json,
   *     "export_2": post_2_json
   *   },
   *   43: {
   *     "export_1": post_1_json
   *   }...
   * }
   *
   * Each post_N_json is potentially a "multi" AnkiConnect
   * post, consisting of "storeMediaFile" and "addNote".
   */
  async function get_post_data(
    anki_connect_url,
    word_ids,
    termid_sentences,
    anki_specs,
  ) {
    const { deck_names, note_types } = anki_specs;
    const postdata = {
      term_ids: word_ids,
      termid_sentences: termid_sentences,
      base_url: window.location.origin,
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
        throw new Error(results.error);
      }

      return results;
    }
    catch (jqXHR) {
      /*
      console.log('jqXHR = ');
      console.log(JSON.stringify(jqXHR, null, 2));
      */
      const errorMessage = jqXHR.responseJSON?.error ||
            jqXHR.responseText ||
            jqXHR.statusText;
      throw new Error(`Failure: ${errorMessage}`);
    }
  }

  /**
   * Each term may have a series of exports to post, e.g.
   * { "export_1": post_1_json, "export_2": post_2_json },
   * and each post_N_json can be several actions, e.g.
   *
   *  {
   *    "export_1": {
   *      "action": "multi",
   *      "params": {
   *        "actions": [
   *          { "action": "storeMediaFile", ... },
   *          { "action": "addNote", ... }
   *        ]
   *      }
   *    },
   *    "export_2": {
   *      "action": "multi",
   *      "params": {
   *        "actions": [
   *          { "action": "storeMediaFile", ... },
   *          { "action": "addNote", ... }
   *        ]
   *      }
   *    },
   *
   * All posts are sent separately, but the results are
   * await all, and so look like this:
   * [
   *   [ post_1_A_result, post_1_B_result ],
   *   [ post_2_A_result, post_2_B_result ],
   * ]
   *
   * e.g.
   * [
   *   // This is the result for "export_1"
   *   ["LUTE_TERM_1.jpg", 1738896726062],
   *   // This is the result for "export_2"
   *   ["LUTE_TERM_2.jpg", { "result": null, "error": "... duplicate" }]
   * ]
   *
   * This maps the export names to the addNote actions, e.g. for the above, returns
   * [
   *   "export_1: success",          // No error in export_1's results
   *   "export_2: "... duplicate"    // error in export_2's results
   * ]
   */
  function _get_addNote_results(name_to_posts, results) {
    // Converts each export name and inner action to an array, e.g.
    // [{ name: "export_1", action: "storeMediaFile" } ... etc
    const name_and_action_array = Object.entries(name_to_posts).flatMap(
      ([name, obj]) =>
      obj.params.actions.map(action => ({ name, action: action.action }))
    );

    // Maps all results to the error message, or success.
    // For the exmaple in the function docs, this would return
    // [ "success", "... duplicate" ]
    const flat_results = results.flat().map(entry => 
      entry && typeof entry === "object" && "error" in entry ?
        entry.error : "success"
    );

    // Adds the final flat_result to its corresponding name_and_action_array.
    for (let i = 0; i < name_and_action_array.length; i++) {
      name_and_action_array[i]["result"] = flat_results[i];
    }

    return name_and_action_array
      .filter(entry => entry.action === "addNote")
      .map(entry => `${entry.name}: ${entry.result}`);
  }


  /**
   * Posts anki cards for the given word_ids, and calls the callback
   * for each.
   *
   * See comments in get_post_data() for notes on its return structure.
   */
  async function post_anki_cards(anki_connect_url, word_ids, termid_sentences, callback) {
    const anki_specs = await get_anki_specs(anki_connect_url);

    const post_data = await get_post_data(
      anki_connect_url,
      word_ids,
      termid_sentences,
      anki_specs
    );

    async function _post_single_card(data) {
      return $.ajax({
        url: anki_connect_url,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        dataType: "json"
      });
    }

    for (const [term_id, name_to_posts] of Object.entries(post_data)) {
      // Continuing the example given in the comments for get_post_data(),
      // if "term_id" = 42,
      // name_to_posts = { "export_1": post_1_json, "export_2": post_2_json }
      const postPromises = Object.values(name_to_posts).
            map(post => _post_single_card(post));
      try {
        const results = await Promise.all(postPromises);
        const addNote_results = _get_addNote_results(name_to_posts, results);
        const msg = addNote_results.length === 0 ?
              "no cards created" :
              addNote_results.join("\n");
        callback(term_id, msg);
      } catch (error) {
        console.error(`Error processing ID ${term_id}:`, error);
        callback(term_id, "Unknown error ...");
      }
    }
  }

  // Exported functions.
  return {
    get_anki_specs: get_anki_specs,
    get_post_data: get_post_data,
    post_anki_cards: post_anki_cards,
  };
})();
