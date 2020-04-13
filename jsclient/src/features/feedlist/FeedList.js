import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import List from '@material-ui/core/List';
import Category from './Category';

import { doFetchFeeds } from './feedSlice';

function mapStateToProps(state) {
  return { categories: state.feeds.categories,
           everLoaded: state.feeds.everLoaded,
           isFoldedFromParent: state.login.isLeftMenuFolded,
           token: state.login.token,
  };
};

const mapDispatchToProps = (dispatch) => ({
  fetchFeed(token) {
      return dispatch(doFetchFeeds(token));
  },
});

function FeedList({ categories, everLoaded, isFoldedFromParent, token, fetchFeed }) {
  useEffect(() => {
    if (!everLoaded) {
      fetchFeed(token);
    }
  });
  return (
    <List>
      {categories.map((category) => (
        <Category key={category.id}
          name={category.name}
          feeds={category.feeds}
          isFoldedFromParent={isFoldedFromParent}
        />
      ))}
    </List>
  );
}

FeedList.propTypes = {
    categories: PropTypes.array.isRequired,
    everLoaded: PropTypes.bool.isRequired,
    isFoldedFromParent: PropTypes.bool.isRequired,
    token: PropTypes.string.isRequired,
    fetchFeed: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
