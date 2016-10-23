var React = require('react');
var NotificationsStore = require('../stores/NotificationsStore');
var NotificationSystem = require('react-notification-system');


var Notifications = React.createClass({
    _notificationSystem: null,
    addNotification: function(notif) {
        this._notificationSystem.addNotification({
                message: notif.message,
                level: notif.level,
                autoDismiss: 30,
                onRemove: this.removeNotification
        });
    },
    removeNotification: function(notif) {
        for(var idx in NotificationsStore.notifs) {
            if(NotificationsStore.notifs[idx].read === false
                    && NotificationsStore.notifs[idx].level === notif.level
                    && NotificationsStore.notifs[idx].message === notif.message) {
                NotificationsStore.notifs[idx].read = true;
                break;
            }

        }
    },
    render: function() {
        return <NotificationSystem ref="notificationSystem" />;
    },
    componentDidMount: function() {
        this._notificationSystem = this.refs.notificationSystem;
        NotificationsStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        NotificationsStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        for(var idx in NotificationsStore.notifs) {
            if(!NotificationsStore.notifs[idx].read) {
                this.addNotification(NotificationsStore.notifs[idx]);
                NotificationsStore.notifs[idx].read = true;
            }
        }
    }
});

module.exports = Notifications;
