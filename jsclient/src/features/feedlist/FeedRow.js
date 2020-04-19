import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ChevronRight from '@material-ui/icons/ChevronRight';

import { doListClusters } from "../clusterlist/clusterSlice";
import feedListStyle from "./feedListStyle";
import { toggleFolding } from "./feedSlice";

function mapStateToProps(state) {
  return { feedListRows: state.feeds.feedListRows.filter((row) => (!row.folded || row.type === "categ" || row.type === "all-categ")),
           isFoldedFromParent: state.feeds.isParentFolded,
           selectedCategoryId: state.clusters.filters["category_id"],
           selectedFeedId: state.clusters.filters["feed_id"],

  };
}

const mapDispatchToProps = (dispatch) => ({
  toggleCatFolding(e, catId) {
    e.stopPropagation();
    return dispatch(toggleFolding(catId));
  },
  listClusters(e, filters) {
    e.stopPropagation();
    return filters.isFolded ? dispatch(toggleFolding(filters.categoryId)) : dispatch(doListClusters(filters));
  },
});

function FeedRow({ index, style, feedListRows,
                   isFoldedFromParent, selectedCategoryId, selectedFeedId,
                   listClusters, toggleCatFolding }) {
  const classes = feedListStyle();
  const obj = feedListRows[index];
  const isSelected = (selectedFeedId === obj.id && obj.type === "feed") || obj.id === selectedCategoryId;

  if (obj.type === "feed") {
    return (
      <ListItem button style={style}
          selected={selectedFeedId === obj.id}
          onClick={(e) => (listClusters(e, { feedId: obj.id }))}
        >
        {obj["icon_url"] ? <img className={classes.feedIcon} alt="feed icon" src={obj["icon_url"]} /> : null}
        <ListItemText primary={obj.str} />
        {obj.unread}
      </ListItem>
    );
  }
  const isAllCateg = obj.type === "all-categ";
  let foldButton;
  if (!isAllCateg) {
    const FoldButton = obj.folded ? ChevronRight : ExpandLess;
    foldButton = <FoldButton onClick={(e) => (toggleCatFolding(e, obj.id))} />;
  }
  return (
    <ListItem button style={style} selected={isSelected}
        onClick={(e) => (listClusters(e, { categoryId: isAllCateg ? "all" : obj.id, isFolded : obj.folded }))}>
      {foldButton}
      <ListItemText primary={isAllCateg ? "All" : obj.str} className={isAllCateg ? classes.catItemAll : null} />
      {obj.unread && !isAllCateg ? obj.unread: null}
    </ListItem>
  );
};

FeedRow.propTypes = {
  index: PropTypes.number.isRequired,
  feedListRows: PropTypes.array.isRequired,
  selectedCategoryId: PropTypes.number,
  selectedFeedId: PropTypes.number,
  listClusters: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedRow);
