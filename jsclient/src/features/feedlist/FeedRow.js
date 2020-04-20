import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import qs from "qs";

import ListItem from "@material-ui/core/ListItem";
import Badge from "@material-ui/core/Badge";
import ListItemText from "@material-ui/core/ListItemText";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ChevronRight from "@material-ui/icons/ChevronRight";
import LinkIcon from "@material-ui/icons/Link";

import { doListClusters } from "../clusterlist/clusterSlice";
import { toggleFolding } from "./feedSlice";
import feedListStyle from "./feedListStyle";
import { apiUrl } from "../../const";

function mapStateToProps(state) {
  return { feedListRows: state.feeds.feedListRows.filter((row) => (
             !row.folded || row.type === "categ" || row.type === "all-categ"
           )),
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
  listClusters(e, filters, isFolded) {
    e.stopPropagation();
    if(isFolded && filters.categoryId){
      dispatch(toggleFolding(filters.categoryId));
    }
    return dispatch(doListClusters(filters));
  },
});

function FeedRow({ index, style, feedListRows,
                   isFoldedFromParent, selectedCategoryId, selectedFeedId,
                   listClusters, toggleCatFolding }) {
  const classes = feedListStyle();
  const obj = feedListRows[index];
  const isSelected = (selectedFeedId === obj.id && obj.type === "feed") || obj.id === selectedCategoryId;
  const badge = <Badge badgeContent={obj.unread} color="primary"></Badge>
  if (obj.type === "feed") {
    let icon;
    if(obj["icon_url"]) {
      icon = <img className={classes.feedIcon} alt="" src={
          apiUrl + "/feed/icon?" + qs.stringify({ url: obj["icon_url"]})} />;
    } else {
      icon = <LinkIcon className={classes.defaultFeedIcon} color="disabled" fontSize="small"/>;
    }
    return (
      <ListItem button style={style}
          className={classes.feedItem}
          selected={selectedFeedId === obj.id}
          onClick={(e) => (listClusters(e, { feedId: obj.id }))}
        >
        {icon}
        <ListItemText primary={obj.str} className={classes.feetItemText}/>
        {badge}
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
        onClick={(e) => (listClusters(e, { categoryId: isAllCateg ? "all" : obj.id}, obj.folded ))}>
      {foldButton}
      <ListItemText primary={isAllCateg ? "All" : obj.str} className={isAllCateg ? classes.catItemAll : null} />
      {obj.unread && !isAllCateg ? badge : null}
    </ListItem>
  );
}

FeedRow.propTypes = {
  index: PropTypes.number.isRequired,
  feedListRows: PropTypes.array.isRequired,
  selectedCategoryId: PropTypes.number,
  selectedFeedId: PropTypes.number,
  listClusters: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedRow);
