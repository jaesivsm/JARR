var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');
var MenuStore = require('../stores/MenuStore');
var MiddlePanelActions = require('../actions/MiddlePanelActions');


var MenuActions = {
    // PARENT FILTERS
    reload: function(set_filter, setFilterFunc, id) {
        jquery.getJSON('/menu', function(payload) {
            var old_all_unread_count = MenuStore.all_unread_count;
            payload.type = ActionTypes.RELOAD_MENU;
            JarrDispatcher.dispatch(payload);
            /* setfilter param is here so were sure it's called in the sole
             * purpose of setting filter and that the setFilterFunc is not
             * some event passed by react
             */
            if(set_filter == 'set_filter' && typeof setFilterFunc == 'function'
                    && (id || id == 0)) {
                setFilterFunc(id);
            /* old_all_unread_count will be -1 on first iteration,
             * so it won't be triggered twice */
            } else if (old_all_unread_count > 0) {
                MiddlePanelActions.reload();
            }
        });
    },
    addCategory: function(name) {
        jquery.ajax({type: 'POST',
                     contentType: 'application/json',
                     data: JSON.stringify({name: name}),
                     url: "api/v2.0/category",
                     success: function () {MenuActions.reload();},
        });
    },
    addFeed: function(url) {
        jquery.ajax({type: 'POST',
                     data: {url: url},
                     url: "/feed/bookmarklet",
                     success: function () {MenuActions.reload();},
        });
    },
    setFilter: function(filter) {
        JarrDispatcher.dispatch({
            type: ActionTypes.MENU_FILTER,
            filter: filter,
        });
    },
    toggleAllFolding: function(all_folded) {
        JarrDispatcher.dispatch({
            type: ActionTypes.TOGGLE_MENU_FOLD,
            all_folded: all_folded,
        });
    }
};

module.exports = MenuActions;
