import React, { useState } from 'react';
import PropTypes from 'prop-types';

import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';

function Category({ id, name, feeds, isFoldedFromParent }) {
  const [isFolded, setIsFolded] = useState(isFoldedFromParent);
  return (
    <>
    <ListItem button key={"button-cat-" + id} onClick={() => (setIsFolded(!isFolded))}>
      <ListItemIcon><InboxIcon /></ListItemIcon>
      <ListItemText primary={name} />
      {!isFolded ? <ExpandLess /> : <ExpandMore />}
    </ListItem>
    <Collapse key={"collapse-cat-" + id} in={!isFolded}>
      <List component="div" disablePadding>
        {feeds.map((feed) => (
          <ListItem button>
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
  id: PropTypes.number.isRequired,
  name: PropTypes.string.isRequired,
  feeds: PropTypes.array.isRequired,
  isFoldedFromParent: PropTypes.bool.isRequired,
};

export default Category;
