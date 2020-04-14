import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';

import { doFetchClusters } from '../clusterlist/clusterSlice';

const mapDispatchToProps = (dispatch) => ({
  fetchClusters(e, filters) {
    e.stopPropagation();
    console.log(filters);
    return dispatch(doFetchClusters(filters));
  },
});

function Category({ id, name, feeds, isFoldedFromParent, fetchClusters }) {
  const [isFolded, setIsFolded] = useState(isFoldedFromParent);
  const FoldButton = isFolded ? ExpandMore : ExpandLess;
  const fold = (e) => {
    e.stopPropagation();
    setIsFolded(!isFolded);
  };
  return (
    <>
    <ListItem button key={"button-cat-" + id}
        onClick={(e) => (fetchClusters(e, { category_id: id }))}>
      <ListItemIcon><InboxIcon /></ListItemIcon>
      <ListItemText primary={name} />
      <FoldButton onClick={fold} />
    </ListItem>
    <Collapse key={"collapse-cat-" + id} in={!isFolded}>
      <List component="div" disablePadding>
        {feeds.map((feed) => (
          <ListItem key={"feed-" + feed.id} button
              onClick={(e) => (fetchClusters(e, { feed_id: feed.id }))}
            >
            <ListItemIcon>
              <StarBorder />
            </ListItemIcon>
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
  isFoldedFromParent: PropTypes.bool.isRequired,
  fetchClusters: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(Category);
