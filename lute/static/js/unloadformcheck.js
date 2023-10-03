/**
 * \file
 * \brief Check for unsaved changes when unloading window.
 * 
 * @package Lute
 * @license unlicense
 * @author  andreask7 <andreasks7@users.noreply.github.com>
 */

/**
 * Set to 1 if a form was altered (set "dirty"), 
 * ask for confirmation before leaving.
 */
var DIRTY = 0;

/**
 * Check the DIRTY status and ask before leaving.
 * 
 * @returns {string} Confiramation string
 */
function askConfirmIfDirty(){
	if (DIRTY) {
		return '** You have unsaved changes! **';
	}
}

/**
 * Set the DIRTY variable to 1.
 */
function makeDirty() {
	DIRTY = 1;
}

/**
 * Set the DIRTY variable to 0
 */
function resetDirty() {
	DIRTY = 0;
}

/**
 * Set DIRTY to 1 if tag object changed.
 * 
 * @param {*}      _  An event, unnused
 * @param {object} ui UI object
 * @returns {true} Always return true
 */
function tagChanged(_, ui) {
	if (!ui.duringInitialization) {
		DIRTY = 1;
	}
	return true;
}

/**
 * Call this function if you want to ask the user 
 * before exiting the form.
 * 
 * @returns {undefined}
 */
function ask_before_exiting() {
	$('#termtags').tagit({
		afterTagAdded: tagChanged, 
		afterTagRemoved: tagChanged
	});
	$('#texttags').tagit({
		afterTagAdded: tagChanged, 
		afterTagRemoved: tagChanged
	}); 
	$('input,checkbox,textarea,radio,select')
	.not('#quickmenu').on('change', makeDirty);
	$(':reset,:submit').on('click', resetDirty);
	$(window).on('beforeunload', askConfirmIfDirty);
} 
