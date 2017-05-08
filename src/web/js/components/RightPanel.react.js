var React = require('react');
var Col = require('react-bootstrap').Col;
var Nav = require('react-bootstrap').Nav;
var Modal = require('react-bootstrap').Modal;
var Button = require('react-bootstrap').Button;
var NavItem = require('react-bootstrap').NavItem;
var Glyphicon = require('react-bootstrap').Glyphicon;
var ButtonGroup = require('react-bootstrap').ButtonGroup;

var RightPanelActions = require('../actions/RightPanelActions');
var RightPanelStore = require('../stores/RightPanelStore');
var MenuStore = require('../stores/MenuStore');
var IconStore = require('../stores/IconStore');
var JarrTime = require('./time.react');

var FeedIcon = require('./icon.react');

var PanelMixin = {
    propTypes: {obj: React.PropTypes.object.isRequired},
    getInitialState: function() {
        return {edit_mode: false, obj: this.props.obj, showModal: false};
    },
    getHeader: function() {
        var icon = null;
        if(this.obj_type == 'feed'){
            icon = <FeedIcon feed_id={this.props.obj.id} />;
        } else if (this.obj_type == 'article') {
            icon = <FeedIcon feed_id={this.props.obj.feed_id} />;
        }
        var btn_grp = null;
        if(this.isEditable() || this.isRemovable()) {
            var edit_button = null;
            if(this.isEditable()) {
                edit_button = (<Button onClick={this.onClickEdit}
                                       title="Click to edit this">
                                 <Glyphicon glyph="pencil" />
                               </Button>);
            }
            var rem_button = null;
            if(this.isRemovable()) {
                rem_button = (<Button onClick={this.onClickRemove}
                                      title="Delete this item">
                                <Glyphicon glyph="trash" />
                              </Button>);
            }
            btn_grp = (<ButtonGroup bsSize="small">
                           {this.getExtraButton()}
                           {edit_button}
                           {rem_button}
                       </ButtonGroup>);
        }
        return (<div id="right-panel-heading" className="panel-heading">
                    <Modal show={this.state.showModal} onHide={this.closeModal}>
                        <Modal.Header closeButton>
                            <Modal.Title>Are you sure ?</Modal.Title>
                        </Modal.Header>
                        <Modal.Footer>
                            <Button onClick={this.confirmDelete}>
                                Confirm
                            </Button>
                        </Modal.Footer>
                    </Modal>

                    <h4>{icon}{this.getTitle()}</h4>
                    {btn_grp}
                </div>);
    },
    getKey: function(prefix, suffix) {
        return ((this.state.edit_mode?'edit':'fix') + prefix
                + '-' + this.props.obj.id + '-' + suffix);
    },
    getCore: function() {
        /* This is a generic constructor for the main part of the right panel
         * information. It will construct a dd / dl structure based on the
         * registered fields of the element and on the mode
         * its currently in (edit / read) */
        var items = [];
        var key, value;
        if(!this.state.edit_mode) {
            this.fields.filter(function(field) {
                        return field.type != 'ignore';
                    }).map(function(field) {
                        value = this.props.obj[field.key];
                        if(field.display_if_empty == false && (value == null || value.length == 0)) {
                            return;
                        }
                        key = this.getKey('dt', field.key);
                        items.push(<dt key={key}>{field.title}</dt>);
                        key = this.getKey('dd', field.key);
                        if(field.type == 'string') {
                            items.push(<dd key={key}>{value}</dd>);
                        } else if(field.type == 'list') {
                            items.push(<dd key={key}>{value.join(', ')}</dd>);
                        } else if(field.type == 'bool') {
                            if(value) {
                                items.push(<dd key={key}><Glyphicon glyph="ok" /></dd>);
                            } else {
                                items.push(<dd key={key}><Glyphicon glyph="pause" /></dd>);
                            }
                        } else if (field.type == 'link') {
                            items.push(<dd key={key}>
                                         <a href={value}>{value}</a>
                                       </dd>);
                        }
                    }.bind(this));
        } else {
            this.fields.filter(function(field) {
                        return field.type != 'ignore';
                    }).map(function(field) {
                        key = this.getKey('dd', field.key);
                        items.push(<dt key={key}>{field.title}</dt>);
                        key = this.getKey('dt', field.key);
                        var input = null;
                        if(field.type == 'string' || field.type == 'link') {
                            input = (<input type="text" name={field.key}
                                            onChange={this.saveField}
                                            defaultValue={this.props.obj[field.key]} />);
                        } else if (field.type == 'bool') {
                            input = (<input type="checkbox" name={field.key}
                                            onChange={this.saveField}
                                            defaultChecked={this.props.obj[field.key]} />);
                        }
                        items.push(<dd key={key}>{input}</dd>);
                    }.bind(this));
        }
        return (<dl className="dl-horizontal">{items}</dl>);
    },
    getSubmit: function() {
        return (<dd key={this.getKey('dd', 'submit')}>
                    <button className="btn btn-default" onClick={this.saveObj}>
                        Submit
                    </button>
                </dd>);
    },
    render: function() {
        return (<div className="panel panel-default">
                    {this.getHeader()}
                    {this.getBody()}
                </div>
        );
    },
    onClickEdit: function() {
        this.setState({edit_mode: !this.state.edit_mode});
    },
    onClickRemove: function() {
        this.setState({showModal: true});
    },
    closeModal: function() {
        this.setState({showModal: false});
    },
    confirmDelete: function() {
        this.setState({showModal: false}, function() {
            RightPanelActions.delObj(this.props.obj.id, this.obj_type);
        }.bind(this));
    },
    saveField: function(evnt) {
        var obj = this.state.obj;
        for(var i in this.fields) {
            if(evnt.target.name == this.fields[i].key) {
                if(this.fields[i].type == 'bool') {
                    obj[evnt.target.name] = evnt.target.checked;
                } else {
                    obj[evnt.target.name] = evnt.target.value;
                }
                break;
            }
        }
        this.setState({obj: obj});
    },
    saveObj: function() {
        var to_push = {};
        this.fields.map(function(field) {
            to_push[field.key] = this.state.obj[field.key];
        }.bind(this));
        this.setState({edit_mode: false}, function() {
            RightPanelActions.putObj(this.props.obj.id, this.obj_type, to_push);
        }.bind(this));
    }
};

var Article = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {return false;},
    isRemovable: function() {return true;},
    fields: [{'title': 'Date', 'type': 'string', 'key': 'date'},
             {'title': 'Original link', 'type': 'link', 'key': 'link'},
             {'title': 'Comments', 'type': 'link', 'key': 'comments',
              'display_if_empty': false},
             {'title': 'Tags', 'type': 'list', 'key': 'tags',
              'display_if_empty': false}
    ],
    obj_type: 'article',
    getTitle: function() {return this.props.obj.title;},
    getExtraButton: function() {
        if(!this.props.obj.readability_available) {
            return null;
        }
        var title;
        if(this.props.obj.readability_parsed) {
            title = "Click here to fetch and parse the article's URL";
        } else {
            title = "This article has been fetched and parsed";
        }
        return (<Button id="readability-reload" onClick={this.reloadParsed}
                        title={title} active={this.props.obj.readability_parsed}>
                    <img src="/static/img/readability.png" />
                </Button>);
    },
    getBody: function() {
        return (<div className="panel-body">
                    {this.getCore()}
                    <div id="article-content" dangerouslySetInnerHTML={
                        {__html: this.props.obj.content}} />
                </div>);
    },
    reloadParsed: function() {
        if(this.props.obj.readability_available
                && !this.props.obj.readability_parsed) {
            RightPanelActions.loadCluster(this.props.obj.cluster_id,
                                          true, true, this.props.obj.id);
        }
    }
});

var Feed = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {return true;},
    isRemovable: function() {return true;},
    obj_type: 'feed',
    fields: [{'title': 'Feed title', 'type': 'string', 'key': 'title'},
             {'title': 'Description', 'type': 'string', 'key': 'description'},
             {'title': 'Feed link', 'type': 'link', 'key': 'link'},
             {'title': 'Site link', 'type': 'link', 'key': 'site_link'},
             {'title': 'Enabled', 'type': 'bool', 'key': 'enabled'},
             {'title': 'Auto parsing',
              'type': 'bool', 'key': 'readability_auto_parse'},
             {'title': 'Reddit integration',
              'type': 'bool', 'key': 'integration_reddit'},
             {'title': 'Filters', 'type': 'ignore', 'key': 'filters'},
             {'title': 'Category', 'type': 'ignore', 'key': 'category_id'}
    ],
    getTitle: function() {return this.props.obj.title;},
    getExtraButton: function() {return null;},
    getFilterRow: function(i, filter) {
        return (<dd key={'d' + i + '-' + this.props.obj.id}
                        className="input-group filter-row">
                <span className="input-group-btn">
                    <button className="btn btn-default" type="button"
                            data-index={i} onClick={this.removeFilterRow}>
                        <Glyphicon glyph='minus' />
                    </button>
                </span>
                <select name="action on" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter['action on']}>
                    <option value="match">match</option>
                    <option value="no match">no match</option>
                </select>
                <input name="pattern" type="text" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.pattern} />
                <select name="type" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.type}>
                    <option value='simple match'>title contains</option>
                    <option value='regex'>title match regex</option>
                    <option value='exact match'>title is</option>
                    <option value='tag match'>one of the tag is</option>
                    <option value='tag contains'>one of the tag contains</option>
                </select>
                <select name="action" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.action}>
                    <option value="mark as read">mark as read</option>
                    <option value="mark as favorite">mark as favorite</option>
                    <option value="skipped">ignore this article</option>
                </select>
            </dd>);
    },
    getFilterRows: function() {
        var rows = [];
        if(this.state.edit_mode) {
            for(var i in this.state.obj.filters) {
                rows.push(this.getFilterRow(i, this.state.obj.filters[i]));
            }
            return (<dl className="dl-horizontal">
                        <dt>Filters</dt>
                        <dd>
                            <button className="btn btn-default"
                                    type="button" onClick={this.addFilterRow}>
                                <Glyphicon glyph='plus' />
                            </button>
                        </dd>
                        {rows}
                    </dl>);
        }
        rows = [];
        rows.push(<dt key={'d-title'}>Filters</dt>);
        for(var i in this.state.obj.filters) {
            rows.push(<dd key={'d' + i}>
                        When {this.state.obj.filters[i]['action on']}
                        on "{this.state.obj.filters[i].pattern}"
                        ({this.state.obj.filters[i].type})
                        "=" {this.state.obj.filters[i].action}
                    </dd>);
        }
        return <dl className="dl-horizontal">{rows}</dl>;
    },
    getCategorySelect: function() {
        var content = null;
        if(this.state.edit_mode) {
            var categ_options = [];
            for(var index in MenuStore.categories_order) {
                var cat_id = MenuStore.categories_order[index];
                categ_options.push(
                        <option value={cat_id}
                                key={MenuStore.categories[cat_id].id}>
                            {MenuStore.categories[cat_id].name}
                        </option>);
            }
            content = (<select name="category_id" className="form-control"
                               onChange={this.saveField}
                               defaultValue={this.props.obj.category_id}>
                            {categ_options}
                       </select>);
        } else {
            content = MenuStore.categories[this.props.obj.category_id].name;
        }
        return (<dl className="dl-horizontal">
                  <dt>Category</dt><dd>{content}</dd>
                </dl>);
    },
    getErrorFields: function() {
        if(this.props.obj.error_count < MenuStore.error_threshold) {
            return;
        }
        if(this.props.obj.error_count < MenuStore.max_error) {
            return (<dl className="dl-horizontal">
                        <dt>State</dt>
                        <dd>The download of this feed has encountered some problems. However its error counter will be reinitialized at the next successful retrieving.</dd>
                        <dt>Last error</dt>
                        <dd>{this.props.obj.last_error}</dd>
                    </dl>);
        }
    return (<dl className="dl-horizontal">
                <dt>State</dt>
                <dd>That feed has encountered too much consecutive errors and won't be retrieved anymore.</dd>

                <dt>Last error</dt>
                <dd>{this.props.obj.last_error}</dd>
                <dd>
                    <Button onClick={this.resetErrors}>Reset error count
                    </Button>
                </dd>
            </dl>);

    },
    resetErrors: function() {
        var obj = this.state.obj;
        obj.error_count = 0;
        this.setState({obj: obj}, function() {
            RightPanelActions.resetErrors(this.props.obj.id);
        }.bind(this));
    },
    getBody: function() {
        return (<div className="panel-body">
                    <dl className="dl-horizontal">
                        <dt>Created on</dt>
                        <dd><JarrTime stamp={this.props.obj.created_rel}
                                      text={this.props.obj.created_date} />
                        </dd>
                        <dt>Last fetched</dt>
                        <dd><JarrTime stamp={this.props.obj.last_rel}
                                      text={this.props.obj.last_retrieved} />
                        </dd>
                    </dl>
                    {this.getErrorFields()}
                    {this.getCategorySelect()}
                    {this.getCore()}
                    {this.getFilterRows()}
                    {this.state.edit_mode?this.getSubmit():null}
                </div>
        );
    },
    addFilterRow: function() {
        var obj = this.state.obj;
        obj.filters.push({action: "mark as read", 'action on': "match",
                      type: "simple match", pattern: ""});
        this.setState({obj: obj});
    },
    removeFilterRow: function(evnt) {
        var obj = this.state.obj;
        obj.filters.splice(evnt.target.getAttribute('data-index'), 1);
        this.setState({obj: obj});
    },
    saveFilterChange: function(evnt) {
        var index = evnt.target.getAttribute('data-index');
        var obj = this.state.obj;
        obj.filters[index][evnt.target.name] = evnt.target.value;
        this.setState({obj: obj});
    }
});

var Category = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {
        if(this.props.obj.id != 0) {return true;}
        else {return false;}
    },
    getExtraButton: function () {return null;},
    isRemovable: function() {return this.isEditable();},
    obj_type: 'category',
    fields: [{'title': 'Category name', 'type': 'string', 'key': 'name'},
             {'title': 'Cluster on title',
              'type': 'bool', 'key': 'cluster_on_title'},
    ],
    getTitle: function() {return this.props.obj.name;},
    getBody: function() {
        return (<div className="panel-body">
                    {this.getCore()}
                    {this.state.edit_mode?this.getSubmit():null}
                </div>);
    }
});

var RightPanel = React.createClass({
    getInitialState: function() {
        return {category: null, feed: null,
                cluster: null, article: null, current: null};
    },
    loadArticle: function(article_id) {
        var article;
        for(var i in this.state.cluster.articles) {
            if(this.state.cluster.articles[i].id == article_id) {
                article = this.state.cluster.articles[i];
                break;
            }
        }
        if(MenuStore.feeds[article.feed_id].readability_auto_parse && !article.readability_parsed) {
            RightPanelActions.loadCluster(article.cluster_id, true, true, article.id);
        } else {
            RightPanelActions.loadArticle(article_id);
        }
    },
    render: function() {
        window.scrollTo(0, 0);
        var content;
        var tabs;
        if(this.state.current == 'cluster') {
            content = (<Article type='article' obj={this.state.article}
                                key={this.state.article.id} />);
            if(this.state.cluster.articles.length > 1) {
                tabs = (<Nav bsStyle="pills" justified
                             activeKey={this.state.article.id}
                             onSelect={this.loadArticle}>
                            {this.state.cluster.articles.map(function(art) {
                                var feed = MenuStore.feeds[art.feed_id];
                                return (<NavItem key={art.id} eventKey={art.id}
                                                 bsStyle="pills" >
                                            <FeedIcon feed_id={feed.id} />
                                            {feed.title}
                                        </NavItem>);
                            })}
                        </Nav>);
            }
        } else if(this.state.current == 'feed') {
            content = (<Feed type='feed' obj={this.state.feed}
                             key={this.state.feed.id} />);
        } else if(this.state.current == 'category') {
            content = (<Category type='category' obj={this.state.category}
                                 key={this.state.category.id} />);
        }

        return (<Col id="right-panel" xsHidden
                        smOffset={4} mdOffset={7} lgOffset={6}
                        sm={8} md={5} lg={6}>
                    {tabs}
                    {content}
                </Col>
        );
    },
    componentDidMount: function() {
        RightPanelStore.addChangeListener(this._onChange);
        IconStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        RightPanelStore.removeChangeListener(this._onChange);
        IconStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState(RightPanelStore.getAll());
    }
});

module.exports = RightPanel;
