var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;

var CHANGE_EVENT = 'change_menu';
var assign = require('object-assign');


var NotificationsStore = assign({}, EventEmitter.prototype, {
    notifs: [],

    addNotifications: function(notifications) {
        var count = this.notifs.length;
        for(var idx in notifications) {
            if(notifications[idx].level && notifications[idx].message) {
                this.notifs.push({
                        key: parseInt(idx, 10) + count,
                        read: false,
                        level: notifications[idx].level,
                        message: notifications[idx].message
                });
            }
        }
    },
    getNotifications: function() {
        this.notifs = this.notifs.filter(function(notif) {return !notif.read;});
        return this.notifs;
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

NotificationsStore.dispatchToken = JarrDispatcher.register(function(action) {
    if(action.notifications) {
        NotificationsStore.addNotifications(action.notifications);
        NotificationsStore.emitChange();
    }
});

module.exports = NotificationsStore;
