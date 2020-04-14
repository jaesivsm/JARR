import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import List from '@material-ui/core/List';
import Category from './Category';

import { doFetchFeeds } from './feedSlice';

function mapStateToProps(state) {
  return { categories: state.feeds.categories,
           isFoldedFromParent: state.login.isLeftMenuFolded,
  };
};

const mapDispatchToProps = (dispatch) => ({
  fetchFeed() {
    return dispatch(doFetchFeeds());
  },
});

function FeedList({ categories, isFoldedFromParent, fetchFeed }) {
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      fetchFeed();
      setEverLoaded(true);
    }
  }, [everLoaded, fetchFeed ]);
  return (
    <List>
      {categories.map((category) => (
        <Category key={"cat-f" + isFoldedFromParent + "-" + category.id}
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
    isFoldedFromParent: PropTypes.bool.isRequired,
    fetchFeed: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
