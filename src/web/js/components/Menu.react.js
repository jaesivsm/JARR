var React = require('react');
var Col = require('react-bootstrap').Col;
var Badge = require('react-bootstrap').Badge;
var Button = require('react-bootstrap').Button;
var ButtonGroup = require('react-bootstrap').ButtonGroup;
var Glyphicon = require('react-bootstrap').Glyphicon;

var MenuStore = require('../stores/MenuStore');
var IconStore = require('../stores/IconStore');
var MenuActions = require('../actions/MenuActions');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var FeedIcon = require('./icon.react');

var FeedItem = React.createClass({
    propTypes: {feed_id: React.PropTypes.number.isRequired,
                title: React.PropTypes.string.isRequired,
                unread: React.PropTypes.number.isRequired,
                error_count: React.PropTypes.number.isRequired,
                active: React.PropTypes.bool.isRequired,
    },
    render: function() {
        var badge_unread = null;
        var icon = <FeedIcon feed_id={this.props.feed_id} />;
        // handling unread badge
        if(this.props.unread){
            badge_unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        // handling it's the selected feed in the menu
        var classes = "nav-feed";
        if(this.props.active) {
            classes += " bg-primary";
        }
        // handling error count displaying
        if(this.props.error_count >= MenuStore.max_error) {
            classes += " bg-danger";
        } else if(this.props.error_count > MenuStore.error_threshold) {
            classes += " bg-warning";
        }
        var title = <span className="title">{this.props.title}</span>;
        return (<li className={classes} onClick={this.handleClick}>
                    {icon}{title}{badge_unread}
                </li>
        );
    },
    // filtering on said feed
    handleClick: function() {
        MiddlePanelActions.setFeedFilter(this.props.feed_id);
    }
});

var Category = React.createClass({
    propTypes: {category_id: React.PropTypes.number,
                active_type: React.PropTypes.string,
                active_id: React.PropTypes.number},
    render: function() {
        var classes = "nav-cat";
        // handling this category being the selected one in the menu
        if((this.props.active_type == 'category_id'
            || this.props.category_id == null)
           && this.props.active_id == this.props.category_id) {
            classes += " bg-primary";
        }
        return (<li className={classes} onClick={this.handleClick}>
                    {this.props.children}
                </li>
        );
    },
    // filtering on said category
    handleClick: function(evnt) {
        // hack to avoid selection when clicking on folding icon
        if(!evnt.target.classList.contains('glyphicon')) {
            if(this.props.category_id != null) {
                MiddlePanelActions.setCategoryFilter(this.props.category_id);
            } else {
                // handling selecting the "all category" item > removing all filters
                MiddlePanelActions.removeParentFilter();
            }
        }
    }
});

var CategoryGroup = React.createClass({
    propTypes: {cat_id: React.PropTypes.number.isRequired,
                filter: React.PropTypes.string.isRequired,
                active_type: React.PropTypes.string,
                active_id: React.PropTypes.number,
                name: React.PropTypes.string.isRequired,
                feeds: React.PropTypes.array.isRequired,
                unread: React.PropTypes.number.isRequired,
                folded: React.PropTypes.bool
    },
    getInitialState: function() {
        return {folded: false};
    },
    componentWillReceiveProps: function(nextProps) {
        if(nextProps.folded != null) {
            this.setState({folded: nextProps.folded});
        }
    },
    render: function() {
        // hidden the "no / 0 category" if empty
        if(!this.props.cat_id && !this.props.feeds.length) {
            return <ul className="hidden" />;
        }
        var filter = this.props.filter;
        var a_type = this.props.active_type;
        var a_id = this.props.active_id;
        if(!this.state.folded) {
            // filtering according to this.props.filter
            var feeds = this.props.feeds.filter(function(feed) {
                if (filter == 'unread' && feed.unread <= 0) {
                    return false;
                } else if (filter == 'error' && feed.error_count <= MenuStore.error_threshold) {
                    return false;
                }
                return true;
            }).sort(function(feed_a, feed_b){
                return feed_b.unread - feed_a.unread;
            }).map(function(feed) {
                return (<FeedItem key={"f" + feed.id} feed_id={feed.id}
                                title={feed.title} unread={feed.unread}
                                error_count={feed.error_count}
                                active={a_type == 'feed_id' && a_id == feed.id} />
                );
            });
        } else {
            var feeds = [];
        }
        var unread = null;
        // displaying unread count
        if(this.props.unread) {
            unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        // folding icon on the right of the category
        var ctrl = (<Glyphicon onClick={this.toggleFolding}
                        glyph={this.state.folded?"menu-right":"menu-down"} />
                    );

        return (<ul className="nav nav-sidebar">
                    <Category category_id={this.props.cat_id}
                              active_id={this.props.active_id}
                              active_type={this.props.active_type}>
                        {ctrl}<h4>{this.props.name}</h4>{unread}
                    </Category>
                    {feeds}
                </ul>
        );
    },
    // handling folding
    toggleFolding: function(evnt) {
        this.setState({folded: !this.state.folded});
        evnt.stopPropagation();
    }
});

var MenuFilter = React.createClass({
    propTypes: {feed_in_error: React.PropTypes.bool,
                filter: React.PropTypes.string.isRequired},
    getInitialState: function() {
        return {allFolded: false};
    },
    render: function() {
        var error_button = null;
        if (this.props.feed_in_error) {
            error_button = (
                    <Button active={this.props.filter == "error"}
                            title="Some of your feeds are in error, click here to list them"
                            onClick={this.setErrorFilter}
                            bsSize="small" bsStyle="warning">
                        <Glyphicon glyph="exclamation-sign" />
                    </Button>
            );
        }
        if(this.state.allFolded) {
            var foldBtnTitle = "Unfold all categories";
            var foldBtnGlyph = "option-horizontal";
        } else {
            var foldBtnTitle = "Fold all categories";
            var foldBtnGlyph = "option-vertical";
        }
        return (<div>
                <ButtonGroup className="nav nav-sidebar">
                    <Button active={this.props.filter == "all"}
                            title="Display all feeds"
                            onClick={this.setAllFilter} bsSize="small">
                        <Glyphicon glyph="menu-hamburger" />
                    </Button>
                    <Button active={this.props.filter == "unread"}
                            title="Display only feed with unread article"
                            onClick={this.setUnreadFilter}
                            bsSize="small">
                        <Glyphicon glyph="unchecked" />
                    </Button>
                    {error_button}
                </ButtonGroup>
                <ButtonGroup className="nav nav-sidebar">
                    <Button onClick={MenuActions.reload}
                            title="Refresh all feeds" bsSize="small">
                        <Glyphicon glyph="refresh" />
                    </Button>
                </ButtonGroup>
                <ButtonGroup className="nav nav-sidebar">
                    <Button title={foldBtnTitle} bsSize="small"
                            onClick={this.toggleFold}>
                        <Glyphicon glyph={foldBtnGlyph} />
                    </Button>
                </ButtonGroup>
                </div>
        );
    },
    setAllFilter: function() {
        MenuActions.setFilter("all");
    },
    setUnreadFilter: function() {
        MenuActions.setFilter("unread");
    },
    setErrorFilter: function() {
        MenuActions.setFilter("error");
    },
    toggleFold: function() {
        this.setState({allFolded: !this.state.allFolded}, function() {
            MenuActions.toggleAllFolding(this.state.allFolded);
        }.bind(this));
    }
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: {}, feeds: {},
                all_folded: false, active_type: null, active_id: null};
    },
    render: function() {
        var feed_in_error = false;
        var rmPrntFilt = (
                <ul className="nav nav-sidebar">
                    <Category category_id={null}
                              active_id={this.state.active_id}
                              active_type={this.state.active_type}>
                        <h4>All</h4>
                    </Category>
                </ul>
        );
        var categories = [];
        for(var index in this.state.categories_order) {
            var cat_id = this.state.categories_order[index];
            var feeds = [];
            var unread = 0;
            this.state.categories[cat_id].feeds.map(function(feed_id) {
                if(this.state.feeds[feed_id].error_count > MenuStore.error_threshold) {
                    feed_in_error = true;
                }
                unread += this.state.feeds[feed_id].unread;
                feeds.push(this.state.feeds[feed_id]);
            }.bind(this));
            categories.push(<CategoryGroup key={"c" + cat_id} feeds={feeds}
                                    filter={this.state.filter}
                                    active_type={this.state.active_type}
                                    active_id={this.state.active_id}
                                    name={this.state.categories[cat_id].name}
                                    cat_id={this.state.categories[cat_id].id}
                                    folded={this.state.all_folded}
                                    unread={unread} />);
        }

        return (<Col xsHidden smHidden md={3} lg={2}
                     id="menu" className="sidebar">
                    <MenuFilter filter={this.state.filter}
                                feed_in_error={feed_in_error} />
                    {rmPrntFilt}
                    {categories}
                </Col>
        );
    },
    componentDidMount: function() {
        var setFilterFunc = null;
        var parent_id = null;
        if(window.location.search.substring(1)) {
            var args = window.location.search.substring(1).split('&');
            args.map(function(arg) {
                if (arg.split('=')[0] == 'at' && arg.split('=')[1] == 'c') {
                    setFilterFunc = MiddlePanelActions.setCategoryFilter;
                } else if (arg.split('=')[0] == 'at' && arg.split('=')[1] == 'f') {
                    setFilterFunc = MiddlePanelActions.setFeedFilter;
                } else if (arg.split('=')[0] == 'ai') {
                    parent_id = parseInt(arg.split('=')[1], 10);
                }
            });
        }
        MenuActions.reload('set_filter', setFilterFunc, parent_id);
        MenuStore.addChangeListener(this._onChange);
        IconStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
        IconStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({filter: datas.filter,
                       feeds: datas.feeds,
                       categories: datas.categories,
                       categories_order: datas.categories_order,
                       active_type: datas.active_type,
                       active_id: datas.active_id,
                       all_folded: datas.all_folded});
    }
});

module.exports = Menu;
