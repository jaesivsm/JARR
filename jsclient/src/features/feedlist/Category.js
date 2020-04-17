import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Collapse from "@material-ui/core/Collapse";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";

import { doListClusters } from "../clusterlist/clusterSlice";
import feedListStyle from "./feedListStyle";

const mapDispatchToProps = (dispatch) => ({
  listClusters(e, filters) {
    e.stopPropagation();
    return dispatch(doListClusters(filters));
  },
});

function toKey(type, id, selectedId) {
  return type + "-" + id + "-" + (id === selectedId ? "selected" : "");
}

function Category(props) {
  const classes = feedListStyle();
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
        key={toKey("button-cat", props.id, props.selectedCategoryId)}
        onClick={(e) => (props.listClusters(e, { categoryId: isAllCateg ? "all" : props.id }))}>
      <ListItemText primary={isAllCateg ? "All" : props.name} />
      {props.unreadCount ? props.unreadCount : null}
      {foldButton}
    </ListItem>
    <Collapse key={"collapse-cat-" + props.id} in={isAllCateg || !isFolded}>
      <List component="div" disablePadding>
        {props.feeds.map((feed) => (
          <ListItem key={toKey("feed-", feed.id, props.selectedFeedId)} button
              selected={props.selectedFeedId === feed.id}
              onClick={(e) => (props.listClusters(e, { feedId: feed.id }))}
            >
            {feed["icon_url"] ? <img className={classes.feedIcon} alt="feed icon" src={feed["icon_url"]} /> : null}
            <ListItemText primary={feed.title} />
            {feed.unreadCount ? feed.unreadCount : null}
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
  unreadCount: PropTypes.number,
  selectedCategoryId: PropTypes.number,
  selectedFeedId: PropTypes.number,
  isFoldedFromParent: PropTypes.bool.isRequired,
  listClusters: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(Category);
