var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');
var MenuStore = require('../stores/MenuStore');


var RightPanelStore = assign({}, EventEmitter.prototype, {
    category: null,
    feed: null,
    cluster: null,
    article: null,
    current: null,
    loadArticle: function(article_id) {
        for(var idx in this.cluster.articles) {
            if(this.cluster.articles[idx].id == article_id) {
                this.article = this.cluster.articles[idx];
                if(this.article.feed_id in MenuStore.feeds && MenuStore.feeds[this.article.feed_id].icon_url) {
                    this.article.icon_url = MenuStore.feeds[this.article.feed_id].icon_url;
                }
                return this.article;
            }
        }
    },
    getAll: function() {
        return {category: this.category, article: this.article,
                feed: this.feed, cluster: this.cluster, current: this.current};
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


RightPanelStore.dispatchToken = JarrDispatcher.register(function(action) {
    switch(action.type) {
        case ActionTypes.LOAD_PARENT:
            RightPanelStore.cluster = null;
            if(action.filter_id == null) {
                RightPanelStore.category = null;
                RightPanelStore.feed = null;
                RightPanelStore.current = null;
            } else if(action.filter_type == 'category_id') {
                RightPanelStore.category = MenuStore.categories[action.filter_id];
                RightPanelStore.feed = null;
                RightPanelStore.current = 'category';
                RightPanelStore.emitChange();
            } else {

                RightPanelStore.feed = MenuStore.feeds[action.filter_id];
                RightPanelStore.category = MenuStore.categories[RightPanelStore.feed.category_id];
                RightPanelStore.current = 'feed';
                RightPanelStore.emitChange();
            }
            break;
        case ActionTypes.LOAD_CLUSTER:
            RightPanelStore.cluster = action.cluster;
            var article;
            if(action.article_id) {
                article = RightPanelStore.loadArticle(action.article_id);
            } else {
                article = RightPanelStore.loadArticle(action.cluster.main_article_id);
            }
            RightPanelStore.article = article;
            RightPanelStore.feed = MenuStore.feeds[article.feed_id];
            RightPanelStore.category = MenuStore.categories[article.category_id];
            RightPanelStore.current = 'cluster';
            RightPanelStore.emitChange();
            break;
        case ActionTypes.LOAD_ARTICLE:
            RightPanelStore.loadArticle(action.article_id);
            RightPanelStore.emitChange();
            break;
        case ActionTypes.RELOAD_MENU:
            RightPanelStore.article = null;
            if(RightPanelStore.category && !(RightPanelStore.category.id.toString() in action.categories)) {
                RightPanelStore.category = null;
                RightPanelStore.current = null;
            }
            if(RightPanelStore.feed && !(RightPanelStore.feed.id.toString() in action.feeds)) {
                RightPanelStore.feed = null;
                RightPanelStore.current = null;
            }
            if(RightPanelStore.current == 'article') {
                RightPanelStore.current = null;
            }
            RightPanelStore.emitChange();
        default:
            // pass
    }
});

module.exports = RightPanelStore;
