var React = require('react');
var Grid = require('react-bootstrap').Grid;

var JarrNavBar = require('./Navbar.react');
var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var RightPanel = require('./RightPanel.react');


var MainApp = React.createClass({
    render: function() {
        return (<div>
                    <JarrNavBar />
                    <Grid fluid id="jarr-container">
                        <Menu />
                        <MiddlePanel />
                        <RightPanel />
                    </Grid>
                </div>
       );
    },
});

module.exports = MainApp;
