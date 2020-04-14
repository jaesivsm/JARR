import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';

import { doFetchClusters } from '../clusterlist/clusterSlice';

const mapDispatchToProps = (dispatch) => ({
  fetchClusters(e, filters) {
    e.stopPropagation();
    return dispatch(doFetchClusters(filters));
  },
});

function toKey(type, id, selectedId) {
  return type + '-' + id + '-' + (id === selectedId ? 'selected' : '');
}

function Category(props) {
  const isAllCateg = !props.id;
  const [isFolded, setIsFolded] = useState(props.isFoldedFromParent);
  /* do not display the All category if not feeds are without a category */
  if (isAllCateg && !props.feeds) { return null; }
  const isSelected = (props.selectedCategoryId === props.id
                    || (!props.selectedCategoryId
                        && !props.selectedFeedId
                        && isAllCateg));
  const fold = (e) => { e.stopPropagation(); setIsFolded(!isFolded); };
  let foldButton;
  if (!isAllCateg) {
    const FoldButton = isFolded ? ExpandMore : ExpandLess;
    foldButton = <FoldButton onClick={fold} />;
  }
  return (
    <>
    <ListItem button selected={isSelected}
        key={toKey('button-cat', props.id, props.selectedCategoryId)}
        onClick={(e) => (props.fetchClusters(e, { categoryId: props.id }))}>
      <ListItemText primary={isAllCateg ? 'All' : props.name} />
      {foldButton}
    </ListItem>
    <Collapse key={"collapse-cat-" + props.id} in={isAllCateg || !isFolded}>
      <List component="div" disablePadding>
        {props.feeds.map((feed) => (
          <ListItem key={toKey("feed-", feed.id, props.selectedFeedId)} button
              selected={props.selectedFeedId === feed.id}
              onClick={(e) => (props.fetchClusters(e, { feedId: feed.id }))}
            >
            <ListItemText primary={feed.title} />
          </ListItem>))}
      </List>
    </Collapse>
    </>
  );
}

Category.propTypes = {
  id: PropTypes.number,
  name: PropTypes.string,
  feeds: PropTypes.array.isRequired,
  selectedCategoryId: PropTypes.number,
  selectedFeedId: PropTypes.number,
  isFoldedFromParent: PropTypes.bool.isRequired,
  fetchClusters: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(Category);
