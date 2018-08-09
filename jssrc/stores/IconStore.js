var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_menu';
var assign = require('object-assign');


var IconStore = assign({}, EventEmitter.prototype, {
    icons: {},
    getIcon: function(feed_id) {
        feed_id = feed_id.toString();
        if(feed_id in this.icons) {
            return this.icons[feed_id];
        }
        return null;
    },
    fillWithFeed: function(feeds) {
        var changed = false;
        for (var idx in feeds) {
            if(!feeds[idx].icon_url) {
                continue;  // no icons
            }
            var feed_id = feeds[idx].id.toString();
            if(feeds[idx].id.toString() in this.icons
               && feeds[idx].icon_url === this.icons[feed_id]) {
                continue;  // icons already in
            }
            this.icons[feed_id] = feeds[idx].icon_url;
            changed = true;
        }
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

IconStore.dispatchToken = JarrDispatcher.register(function(action) {
    var changed = false;
    switch(action.type) {
        case ActionTypes.RELOAD_MENU:
            changed = IconStore.fillWithFeed(action.feeds);
            break;
        default:
            // do nothing
    }
    if(changed) {
        IconStore.emitChange();
    }
});

module.exports = IconStore;
