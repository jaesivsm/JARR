var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_menu';
var assign = require('object-assign');


var MenuStore = assign({}, EventEmitter.prototype, {
    filter: 'all',  // menu filter among "all" and "unread"
    feeds: {},  // feeds with their ids as key
    categories: {},  // categories with their ids as key
    categories_order: [],
    active_type: null,
    active_id: null,
    is_admin: false,
    crawling_method: 'http',
    all_unread_count: -1,
    max_error: 0,
    error_threshold: 0,
    all_folded: false,

    getAll: function() {
        return this;
    },
    setFilter: function(value) {
        if(this.filter != value) {
            this.filter = value;
            return true;
        }
        return false;
    },
    setActive: function(type, value) {
        if(this.active_id != value || this.active_type != type) {
            this.active_type = type;
            this.active_id = value;
            return true;
        }
        return false;
    },
    readCluster: function(cluster, value) {
        cluster.feeds_id.map(function(feed_id) {
            this.feeds[feed_id].unread += value;
            if(this.feeds[feed_id].category_id) {
                this.categories[this.feeds[feed_id].category_id].unread += value;
            }
        }.bind(this));
    },
    emitChange: function(all_folded) {
        if (all_folded == true || all_folded == false) {
            this.all_folded = all_folded;
        } else {
            this.all_folded = null;
        }
        this.emit(CHANGE_EVENT);
    },
    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },
    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
});


MenuStore.dispatchToken = JarrDispatcher.register(function(action) {
    switch(action.type) {
        case ActionTypes.RELOAD_MENU:
            MenuStore.feeds = action.feeds;
            MenuStore.categories = action.categories;
            MenuStore.categories_order = action.categories_order;
            MenuStore.is_admin = action.is_admin;
            MenuStore.max_error = action.max_error;
            MenuStore.error_threshold = action.error_threshold;
            MenuStore.crawling_method = action.crawling_method;
            MenuStore.all_unread_count = action.all_unread_count;
            MenuStore.emitChange();
            break;
        case ActionTypes.PARENT_FILTER:
            var changed = MenuStore.setActive(action.filter_type, action.filter_id);
            if(action.filters && action.clusters && !action.filters.query
                    && action.filters.filter == 'unread') {
                var new_unread = {};
                action.clusters.map(function(cluster) {
                    cluster.feeds_id.map(function(feed_id) {
                        if(!(feed_id in new_unread)) {
                            new_unread[feed_id] = 0;
                        }
                        if(!cluster.read) {
                            new_unread[feed_id] += 1;
                        }
                    });
                });
                for(var feed_id in new_unread) {
                    var cat_id = MenuStore.feeds[feed_id].category_id;
                    var old_unread = MenuStore.feeds[feed_id].unread;
                    if(old_unread > new_unread[feed_id]) {
                        continue;
                    }
                    changed = true;
                    if((MenuStore.active_type == 'feed_id'
                            && MenuStore.active_id == feed_id)
                            || (MenuStore.active_type == 'category_id'
                                && MenuStore.active_id == cat_id)
                            || (MenuStore.active_type === null)) {
                        MenuStore.feeds[feed_id].unread = new_unread[feed_id];
                        MenuStore.categories[cat_id].unread -= old_unread;
                        MenuStore.categories[cat_id].unread += new_unread[feed_id];
                    }
                }
            }
            if(changed) {MenuStore.emitChange();}
            break;
        case ActionTypes.MENU_FILTER:
            if (MenuStore.setFilter(action.filter)) {
                MenuStore.emitChange();
            }
            break;
        case ActionTypes.CHANGE_ATTR:
            if(action.attribute != 'read') {
                return;
            }
            action.clusters.map(function(cluster) {
                MenuStore.readCluster(cluster, action.value_num);
            });
            MenuStore.emitChange();
            break;
        case ActionTypes.LOAD_CLUSTER:
            if(!action.was_read_before) {
                MenuStore.readCluster(action.cluster, -1);
                MenuStore.emitChange();
            }
            break;
        case ActionTypes.TOGGLE_MENU_FOLD:
            MenuStore.emitChange(action.all_folded);
            break;
        case ActionTypes.MARK_ALL_AS_READ:
            action.clusters.map(function(cluster) {
                if(!cluster.read) {
                    MenuStore.readCluster(cluster, -1);
                }
            });
            MenuStore.emitChange();
            break;
        default:
            // do nothing
    }
});

module.exports = MenuStore;
