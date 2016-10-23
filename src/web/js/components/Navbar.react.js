var React = require('react');
var Glyphicon = require('react-bootstrap').Glyphicon;
var Nav = require('react-bootstrap').Nav;
var NavItem = require('react-bootstrap').NavItem;
var Navbar = require('react-bootstrap').Navbar;
var NavDropdown = require('react-bootstrap').NavDropdown;
var MenuItem = require('react-bootstrap').MenuItem;
var Modal = require('react-bootstrap').Modal;
var Button = require('react-bootstrap').Button;
var Input = require('react-bootstrap').Input;

var MenuStore = require('../stores/MenuStore');
var MenuActions = require('../actions/MenuActions');

JarrNavBar = React.createClass({
    getInitialState: function() {
        return {is_admin: MenuStore.is_admin,
                crawling_method: MenuStore.crawling_method,
                showModal: false, modalType: null, modalValue: null};
    },
    sectionAdmin: function() {
        if(this.state.is_admin) {
            return (<MenuItem href="/admin/dashboard">
                        <Glyphicon glyph="dashboard" />Dashboard
                    </MenuItem>);
        }
    },
    getModal: function() {
        var heading = null;
        var body = null;
        if(this.state.modalType == 'addFeed') {
            heading = 'Add a new feed';
            placeholder = "Site or feed url, we'll sort it out later ;)";
            body = <Input name="url" type="text" required
                          onChange={this.handleModalChange}
                          placeholder={placeholder} />;
        } else if (this.state.modalType == 'addCategory') {
            heading = 'Add a new category';
            body = <Input name="name" type="text" required
                          onChange={this.handleModalChange}
                          placeholder="Name, there isn't much more to it" />;
        }
        return (<Modal show={this.state.showModal} onHide={this.close}>
                  <form onSubmit={this.submit}>
                    <Modal.Header closeButton>
                      <Modal.Title>{heading}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                      {body}
                    </Modal.Body>
                    <Modal.Footer>
                      <Button type="submit">Add</Button>
                    </Modal.Footer>
                  </form>
                </Modal>);
    },
    handleModalChange: function(evnt) {
        this.setState({modalValue: evnt.target.value});
    },
    submit: function(evnt) {
        if(this.state.modalType == 'addCategory') {
            MenuActions.addCategory(this.state.modalValue);
        } else {
            MenuActions.addFeed(this.state.modalValue);
        }
        evnt.preventDefault()
        this.close();
    },
    close: function() {
        this.setState({showModal: false, modalType: null, modalValue: null});
    },
    openAddFeed: function() {
        this.setState({showModal: true, modalType: 'addFeed'});
    },
    openAddCategory: function() {
        this.setState({showModal: true, modalType: 'addCategory'});
    },
    render: function() {
        return (<Navbar fixedTop inverse id="jarrnav" fluid staticTop={true}>
                    {this.getModal()}
                    <Navbar.Header>
                        <Navbar.Brand>
                            <a href="/">JARR</a>
                        </Navbar.Brand>
                        <Navbar.Toggle />
                    </Navbar.Header>
                    <Navbar.Collapse>
                    <Nav pullRight>
                        <NavItem className="jarrnavitem"
                                 onClick={this.openAddFeed} href="#">
                            <Glyphicon glyph="plus-sign" />Add a new feed
                        </NavItem>
                        <NavItem className="jarrnavitem"
                                 onClick={this.openAddCategory} href="#">
                            <Glyphicon glyph="plus-sign" />Add a new category
                        </NavItem>
                        <NavDropdown title="Feed" id="feed-dropdown">
                            <MenuItem href="/feeds/inactives">
                                Inactives
                            </MenuItem>
                            <MenuItem href="/articles/history">
                                History
                            </MenuItem>
                            <MenuItem href="/feeds/">
                                All
                            </MenuItem>
                        </NavDropdown>
                        <NavDropdown title={<Glyphicon glyph='user' />}
                                id="user-dropdown">
                            <MenuItem href="/user/profile">
                                <Glyphicon glyph="user" />Profile
                            </MenuItem>
                            <MenuItem href="/about">
                                <Glyphicon glyph="question-sign" />About
                            </MenuItem>
                            {this.sectionAdmin()}
                            <MenuItem href="/logout">
                                <Glyphicon glyph="log-out" />Logout
                            </MenuItem>
                        </NavDropdown>
                    </Nav>
                    </Navbar.Collapse>
                </Navbar>
        );
    },
    componentDidMount: function() {
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({is_admin: datas.is_admin,
                       crawling_method: datas.crawling_method});
    }
});

module.exports = JarrNavBar;
