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
    result = await _invoke(anki_connect_url, p);
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
    result = await _invoke(anki_connect_url, p);

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

  async function get_anki_specs(anki_connect_url) {
    return _get_anki_specs(anki_connect_url)
      .then(result => {
        // console.log("result:", result);
        return result;
      })
      .catch(error => {
        console.log("Error getting specs");
        return null;
      });
  }

  async function get_post_data(anki_connect_url, word_ids) {
    // console.log("getting post data");

    const anki_specs = await get_anki_specs(anki_connect_url);
    // console.log("got specs?", anki_specs);

    if (!anki_specs) {
      console.log("Anki not running, or can't connect?");
      return null;
    }

    const { deck_names, note_types } = anki_specs;
    const postdata = {
      term_ids: word_ids,
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
        return null;
      }

      return results;
    }
    catch (jqXHR) {
      console.error("AJAX request failed:", jqXHR.responseText || jqXHR.statusText);
      return null;
    }
  }

  async function post_anki_cards(anki_connect_url, word_ids, callback) {
    const post_data = await get_post_data(anki_connect_url, word_ids);
    if (post_data == null) {
      console.log("anki not running? can't connect?")
      return;
    }

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
      if (Object.keys(name_to_posts).length === 0) {
        // No posts, just call the callback
        callback(id, 'no cards created');
        continue;
      }

      console.log("*******************");
      console.log(JSON.stringify(name_to_posts, null, 2));
      console.log("*******************");

      const name_and_action_array = Object.entries(name_to_posts).flatMap(
        ([name, obj]) =>
        obj.params.actions.map(action => ({ name, action: action.action }))
      );

      const export_posts = Object.values(name_to_posts);
      const postPromises = export_posts.map(post => _post_single_card(post));
      try {
        const results = await Promise.all(postPromises);
        const flat_results = results.flat();
        const final_flat_results = flat_results.map(entry => 
          entry && typeof entry === "object" && "error" in entry ? entry.error : "success"
        );
        for (let i = 0; i < name_and_action_array.length; i++) {
          name_and_action_array[i]["result"] = final_flat_results[i];
        }
        const addNote_results = name_and_action_array
              .filter(entry => entry.action === "addNote")
              .map(entry => `${entry.name}: ${entry.result}`);

        console.log('==================');
        console.log(JSON.stringify(name_and_action_array, null, 2));
        console.log(JSON.stringify(flat_results, null, 2));
        console.log(JSON.stringify(final_flat_results, null, 2));
        console.log(JSON.stringify(addNote_results, null, 2));
        console.log('================');
        callback(term_id, addNote_results.join("\n"));
      } catch (error) {
        console.error(`Error processing ID ${term_id}:`, error);
        callback(id, null); // Call callback with null to indicate failure
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
