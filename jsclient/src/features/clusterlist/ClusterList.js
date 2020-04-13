import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

function mapStateToProps(state) {
    return {};
};

function FeedList({ feeds }) {
    return (<div />);
}

FeedList.propTypes = {
    feeds: PropTypes.array.isRequired,
}

export default connect(mapStateToProps)(FeedList);
