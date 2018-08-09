var React = require('react');
var Glyphicon = require('react-bootstrap').Glyphicon;
var IconStore = require('../stores/IconStore');


var FeedIcon = React.createClass({
    propTypes: {feed_id: React.PropTypes.number.isRequired},
    getInitialState: function() {
        return {icon_url: IconStore.getIcon(this.props.feed_id)};
    },
    render: function() {
        if(this.state.icon_url){
            return <img width="16px" src={this.state.icon_url} />;
        } else {
            return <Glyphicon glyph="ban-circle" />;
        }
    },
    componentWillReceiveProps: function(nextProps){
        this.setState({icon_url: IconStore.getIcon(this.props.feed_id)});
    }
});

module.exports = FeedIcon;
