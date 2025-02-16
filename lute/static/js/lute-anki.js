/* Posting to Anki via AnkiConnect. */

const LuteAnki = (function() {

  /* copied verbatim from
   * https://foosoft.net/projects/anki-connect/index.html#miscellaneous-actions */
  function _invoke(action, version, params={}) {
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
        xhr.send(JSON.stringify({action, version, params}));
    });
  }

  return {
    /**
     * Queries anki and gets data.
     */
    get_anki_specs: async function(anki_connect_url) {
      const result = await _invoke('deckNames', 6);
      console.log(`got list of decks: ${result}`);
    }
  };

})();
