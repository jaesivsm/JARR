var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');
var MiddlePanelStore = require('../stores/MiddlePanelStore');

var reloadIfNecessaryAndDispatch = function(dispath_payload) {
    var filters = MiddlePanelStore.getRequestFilter(dispath_payload.display_search);
    MiddlePanelStore.filter_whitelist.map(function(key) {
        if(key in dispath_payload) {
            filters[key] = dispath_payload[key];
        }
        if(filters[key] == null) {
            delete filters[key];
        }
    });
    if('display_search' in filters) {
        delete filters['display_search'];
    }
    jquery.getJSON('/middle_panel', filters,
            function(payload) {
                dispath_payload.clusters = payload.clusters;
                dispath_payload.filters = filters;
                JarrDispatcher.dispatch(dispath_payload);
    });
}


var MiddlePanelActions = {
    reload: function() {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.RELOAD_MIDDLE_PANEL,
        });
    },
    search: function(search) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.RELOAD_MIDDLE_PANEL,
            display_search: true,
            query: search.query,
            search_title: search.title,
            search_content: search.content,
        });
    },
    search_off: function() {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.RELOAD_MIDDLE_PANEL,
            display_search: false,
        });
    },
    removeParentFilter: function() {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: null,
            filter_id: null,
        });
    },
    setCategoryFilter: function(category_id) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: 'category_id',
            filter_id: category_id,
        });
    },
    setFeedFilter: function(feed_id) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: 'feed_id',
            filter_id: feed_id,
        });
    },
    setFilter: function(filter) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.MIDDLE_PANEL_FILTER,
            filter: filter,
        });
    },
    changeRead: function(cluster_id, new_value){
        var read_reason = new_value ? 'marked' : null;
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({read: new_value, read_reason: read_reason}),
                url: "api/v2.0/cluster/" + cluster_id,
                success: function (payload) {
                    MiddlePanelActions.changeAttr(cluster_id, 'read', new_value, payload.categories_id, payload.feeds_id);
                },
        });
    },
    changeAttr: function(cluster_id, attr, new_value, categories_id, feeds_id) {
        JarrDispatcher.dispatch({
            type: ActionTypes.CHANGE_ATTR,
            attribute: attr,
            value_bool: new_value,
            value_num: new_value ? -1 : 1,
            clusters: [{cluster_id: cluster_id, categories_id: categories_id, feeds_id: feeds_id}],
        });
    },
    changeLike: function(cluster_id, new_value){
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({liked: new_value}),
                url: "api/v2.0/cluster/" + cluster_id,
                success: function (payload) {
                    MiddlePanelActions.changeAttr(cluster_id, 'liked', new_value, payload.categories_id, payload.feeds_id);
                },
        });
    },
    markAllAsRead: function() {
        var filters = MiddlePanelStore.getRequestFilter();
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(filters),
                url: "/mark_all_as_read",
                success: function (payload) {
                    JarrDispatcher.dispatch({
                        type: ActionTypes.MARK_ALL_AS_READ,
                        clusters: payload.clusters,
                    });
                },
        });
    }
};

module.exports = MiddlePanelActions;
