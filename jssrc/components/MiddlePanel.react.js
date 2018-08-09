var React = require('react');

var Col = require('react-bootstrap').Col;
var Row = require('react-bootstrap').Row;
var Panel = require('react-bootstrap').Panel;
var Button = require('react-bootstrap').Button;
var ButtonGroup = require('react-bootstrap').ButtonGroup;
var Glyphicon = require('react-bootstrap').Glyphicon;

var MenuStore = require('../stores/MenuStore');
var IconStore = require('../stores/IconStore');
var MiddlePanelStore = require('../stores/MiddlePanelStore');
var MiddlePanelActions = require('../actions/MiddlePanelActions');
var RightPanelActions = require('../actions/RightPanelActions');

var JarrTime = require('./time.react');
var FeedIcon = require('./icon.react');

var TableLine = React.createClass({
    propTypes: {cluster_id: React.PropTypes.number.isRequired,
                main_article_id: React.PropTypes.number.isRequired,
                feed_title: React.PropTypes.string.isRequired,
                title: React.PropTypes.string.isRequired,
                rel_date: React.PropTypes.string.isRequired,
                date: React.PropTypes.string.isRequired,
                read: React.PropTypes.bool.isRequired,
                selected: React.PropTypes.bool.isRequired,
                liked: React.PropTypes.bool.isRequired,
                feeds_id: React.PropTypes.array.isRequired
    },
    getInitialState: function() {
        return {read: this.props.read, liked: this.props.liked, selected: false};
    },
    render: function() {
        var liked = this.state.liked ? 'l' : '';
        var title = (<a href={'/cluster/redirect/' + this.props.cluster_id}
                        onClick={this.openRedirectLink} target="_blank"
                        title={this.props.feed_title}>
                        {this.props.feeds_id.map(function(feed_id) {
                            return <FeedIcon key={feed_id} feed_id={feed_id} />;
                        })}
                        {this.props.feed_title}
                     </a>);
        var read = (<Glyphicon glyph={this.state.read?"check":"unchecked"}
                               onClick={this.toogleRead} />);
        var liked = (<Glyphicon glyph={this.state.liked?"star":"star-empty"}
                                onClick={this.toogleLike} />);
        icon = <Glyphicon glyph={"new-window"} />;
        var clsses = "list-group-item";
        if(this.props.selected) {
            clsses += " active";
        }
        return (<div className={clsses} onClick={this.loadCluster} title={this.props.title}>
                    <span>{title}</span>
                    <JarrTime text={this.props.date} stamp={this.props.rel_date} />
                    <div>{read} {liked} {this.props.title}</div>
                </div>
        );
    },
    openRedirectLink: function(evnt) {
        this.setState({read: true}, function() {
          MiddlePanelActions.changeAttr(this.props.cluster_id, 'read', true,
            this.props.feeds_id.map(function(feed_id) {
              return MenuStore.feeds[feed_id].category_id}),
            this.props.feeds_id);
        }.bind(this));
        evnt.stopPropagation();
    },
    toogleRead: function(evnt) {
        this.setState({read: !this.state.read}, function() {
            MiddlePanelActions.changeRead(this.props.cluster_id, this.state.read);
        }.bind(this));
        evnt.stopPropagation();
    },
    toogleLike: function(evnt) {
        this.setState({liked: !this.state.liked}, function() {
            MiddlePanelActions.changeLike(this.props.cluster_id, this.state.liked);
        }.bind(this));
        evnt.stopPropagation();
    },
    loadCluster: function() {
        this.setState({selected: true, read: true}, function() {
            RightPanelActions.loadCluster(this.props.cluster_id, this.props.read);
        }.bind(this));
    },
    stopPropagation: function(evnt) {
        evnt.stopPropagation();
    }
});

var MiddlePanelSearchRow = React.createClass({
    getInitialState: function() {
        return {query: MiddlePanelStore.query,
                search_title: MiddlePanelStore.search_title,
                search_content: MiddlePanelStore.search_content
        };
    },
    render: function() {
        return (<Row>
                    <form onSubmit={this.launchSearch}>
                    <div className="input-group input-group-sm">
                        <span className="input-group-addon">
                            <span onClick={this.toogleSTitle}>Title</span>
                            <input id="search-title" type="checkbox"
                                   onChange={this.toogleSTitle}
                                   checked={this.state.search_title}
                                   aria-label="Search title" />
                        </span>
                        <span className="input-group-addon">
                            <span onClick={this.toogleSContent}>Content</span>
                            <input id="search-content" type="checkbox"
                                   onChange={this.toogleSContent}
                                   checked={this.state.search_content}
                                   aria-label="Search content" />
                        </span>
                        <input type="text" className="form-control"
                               onChange={this.setQuery}
                               placeholder="Search text" />
                    </div>
                    </form>
                </Row>
        );
    },
    setQuery: function(evnt) {
        this.setState({query: evnt.target.value});
    },
    toogleSTitle: function() {
        this.setState({search_title: !this.state.search_title},
                      this.launchSearch);
    },
    toogleSContent: function() {
        this.setState({search_content: !this.state.search_content},
                      this.launchSearch);
    },
    launchSearch: function(evnt) {
        if(this.state.query && (this.state.search_title
                             || this.state.search_content)) {
            MiddlePanelActions.search({query: this.state.query,
                                       title: this.state.search_title,
                                       content: this.state.search_content});
        }
        if(evnt) {
            evnt.preventDefault();
        }
    }
});

var MiddlePanelParentFilterRow = React.createClass({
    getInitialState: function() {
        return {id: null, type: null, title: null};
    },
    render: function() {
        var cn;
        var img;
        var content = "Selected ";
        if (this.state.type == 'feed_id') {
            content += "Feed: " + this.state.title;
            img = <FeedIcon key={this.state.id} feed_id={this.state.id} />;
        } else if (this.state.type == 'category_id') {
            content += "Category: " + this.state.title;
        } else {
            cn = "hidden";
        }
        return (<Panel className={cn} onClick={this.showParent}>
                    {img}
                    {content}
                </Panel>);
    },
    showParent: function(evnt) {
        RightPanelActions.loadParent(this.state.type, this.state.id);
    },
    componentDidMount: function() {
        MenuStore.addChangeListener(this._onChange);
        IconStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
        IconStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var new_state = {id: MenuStore.active_id, title: null,
                         type: MenuStore.active_type};
        if (new_state.type == 'feed_id' && new_state.id in MenuStore.feeds) {
            new_state.title = MenuStore.feeds[new_state.id].title;
        } else if (new_state.type == 'category_id'
                   && new_state.id in MenuStore.categories) {
            new_state.title = MenuStore.categories[new_state.id].name;
        }
        this.setState(new_state);
    }
});

var MiddlePanelFilter = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore.filter,
                display_search: MiddlePanelStore.display_search};
    },
    render: function() {
        var search_row = null;
        if(this.state.display_search) {
            search_row = <MiddlePanelSearchRow />
        }
        return (<div>
                <Row className="show-grid">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                title="Display all clusters"
                                onClick={this.setAllFilter} bsSize="small">
                            <Glyphicon glyph="menu-hamburger" />
                        </Button>
                        <Button active={this.state.filter == "unread"}
                                title="Display only unread clusters"
                                onClick={this.setUnreadFilter}
                                bsSize="small">
                            <Glyphicon glyph="unchecked" />
                        </Button>
                        <Button active={this.state.filter == "liked"}
                                title="Filter only liked clusters"
                                onClick={this.setLikedFilter}
                                bsSize="small">
                            <Glyphicon glyph="star" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onClick={this.toogleSearch}
                                title="Search through displayed clusters"
                                bsSize="small">
                            <Glyphicon glyph="search" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onClick={MiddlePanelActions.markAllAsRead}
                                title="Mark all displayed clusters as read"
                                bsSize="small">
                            <Glyphicon glyph="remove-sign" />
                        </Button>
                    </ButtonGroup>
                </Row>
                {search_row}
                </div>
        );
    },
    setAllFilter: function() {
        this.setState({filter: 'all'}, function() {
            MiddlePanelActions.setFilter('all');
        }.bind(this));
    },
    setUnreadFilter: function() {
        this.setState({filter: 'unread'}, function() {
            MiddlePanelActions.setFilter('unread');
        }.bind(this));
    },
    setLikedFilter: function() {
        this.setState({filter: 'liked'}, function() {
            MiddlePanelActions.setFilter('liked');
        }.bind(this));
    },
    toogleSearch: function() {
        this.setState({display_search: !this.state.display_search},
            function() {
                if(!this.state.display_search) {
                    MiddlePanelActions.search_off();
                }
            }.bind(this)
        );
    }
});

var ClusterList = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore.filter, clusters: []};
    },
    render: function() {
        return (<Row className="show-grid">
                    <div className="list-group">
                    {this.state.clusters.map(function(cluster){
                        var key = "clu" + cluster.id;
                        if(cluster.read) {key+="r";}
                        if(cluster.liked) {key+="l";}
                        if(cluster.selected) {key+="s";}
                        return (<TableLine key={key}
                                        title={cluster.main_title}
                                        read={cluster.read}
                                        liked={cluster.liked}
                                        rel_date={cluster.rel_date}
                                        date={cluster.date}
                                        selected={cluster.selected}
                                        cluster_id={cluster.id}
                                        main_article_id={cluster.main_article_id}
                                        feeds_id={cluster.feeds_id}
                                        locales={['en']}
                                        feed_title={cluster.main_feed_title} />);})}
                    </div>
                </Row>
        );
    },
    componentDidMount: function() {
        MiddlePanelActions.reload();
        MiddlePanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MiddlePanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState({filter: MiddlePanelStore.filter,
                       clusters: MiddlePanelStore.getClusters()});
    }
});

var MiddlePanel = React.createClass({
    render: function() {
        return (<Col id="middle-panel" mdOffset={3} lgOffset={2}
                                       xs={12} sm={4} md={4} lg={4}>
                    <MiddlePanelParentFilterRow />
                    <MiddlePanelFilter />
                    <ClusterList />
                </Col>
        );
    }
});

module.exports = MiddlePanel;
