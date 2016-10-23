var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');


var MiddlePanelStore = assign({}, EventEmitter.prototype, {
    filter_whitelist: ['filter', 'filter_id', 'filter_type', 'display_search',
                       'query', 'search_title', 'search_content'],
    clusters: [],
    selected_cluster: null,
    filter: 'unread',
    filter_type: null,
    filter_id: null,
    display_search: false,
    query: null,
    search_title: true,
    search_content: false,

    getRequestFilter: function(display_search) {
        var filters = {'filter': this.filter,
                       'filter_type': this.filter_type,
                       'filter_id': this.filter_id,
        };
        if(display_search || (display_search == undefined && this.display_search)) {
            filters.query = this.query;
            filters.search_title = this.search_title;
            filters.search_content = this.search_content;
        };
        return filters;
    },
    getClusters: function() {
        var key = null;
        var id = null;
        if (this.filter_type == 'feed_id') {
            key = 'feeds_id';
            id = this.filter_id;
        } else if (this.filter_type == 'category_id') {
            key = 'categories_id';
            id = this.filter_id;
        }
        return this.clusters
        .map(function(cluster) { // marking cluster as selected or not selected
            if(cluster.id == this.selected_cluster) {
                cluster.selected = true;
            } else if(cluster.selected) {
                cluster.selected = false;
            }
            return cluster;
        }.bind(this))
        .filter(function(cluster) {  // applying set filters on cluster list
            return (cluster.selected || ((!key || cluster[key].indexOf(id) > -1)
                    && (this.filter == 'all'
                        || (this.filter == 'unread' && !cluster.read)
                        || (this.filter == 'liked' && cluster.liked))));
        }.bind(this));
    },
    setClusters: function(clusters) {
        if(clusters || clusters == []) {
            this.clusters = clusters;
            return true;
        }
        return false;
    },
    registerFilter: function(action) {
        var changed = false;
        this.filter_whitelist.map(function(key) {
            if(key in action && this[key] != action[key]) {
                changed = true;
                this[key] = action[key];
            }
        }.bind(this));
        return changed;
    },
    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },
    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },
    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
});


MiddlePanelStore.dispatchToken = JarrDispatcher.register(function(action) {
    var changed = false;
    if (action.type == ActionTypes.RELOAD_MIDDLE_PANEL
            || action.type == ActionTypes.PARENT_FILTER
            || action.type == ActionTypes.MIDDLE_PANEL_FILTER) {
        changed = MiddlePanelStore.registerFilter(action);
        changed = MiddlePanelStore.setClusters(action.clusters) || changed;
    } else if (action.type == ActionTypes.MARK_ALL_AS_READ) {
        changed = MiddlePanelStore.registerFilter(action);
        for(var i in action.clusters) {
            action.clusters[i].read = true;
        }
        changed = MiddlePanelStore.setClusters(action.clusters) || changed;
    } else if (action.type == ActionTypes.CHANGE_ATTR) {
        var attr = action.attribute;
        var val = action.value_bool;
        action.clusters.map(function(cluster) {
            for (var i in MiddlePanelStore.clusters) {
                if(MiddlePanelStore.clusters[i].id == cluster.cluster_id) {
                    if (MiddlePanelStore.clusters[i][attr] != val) {
                        MiddlePanelStore.clusters[i][attr] = val;
                        // avoiding redraw if not filter, display won't change anyway
                        if(MiddlePanelStore.filter != 'all') {
                            changed = true;
                        }
                    }
                    break;
                }
            }
        });
    } else if (action.type == ActionTypes.LOAD_CLUSTER) {
        changed = true;
        MiddlePanelStore.selected_cluster = action.cluster.id;
        for (var i in MiddlePanelStore.clusters) {
            if(MiddlePanelStore.clusters[i].id == action.cluster.id) {
                MiddlePanelStore.clusters[i].read = true;
                break;
            }
        }
    }
    if(changed) {MiddlePanelStore.emitChange();}
});

module.exports = MiddlePanelStore;
