import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui component
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import ListItem from "@material-ui/core/ListItem";
import Badge from "@material-ui/core/Badge";
import ListItemText from "@material-ui/core/ListItemText";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";
// jarr
import doListClusters from "../../hooks/doListClusters";
import { toggleMenu, toggleFolding } from "./slice";
import feedListStyle from "./feedListStyle";
import FeedIcon from "../../components/FeedIcon";

function mapStateToProps(state) {
  return { feedListRows: state.feeds.feedListRows.filter(state.feeds.feedListFilter),
           isFoldedFromParent: state.feeds.isParentFolded,
           selectedCategoryId: state.clusters.filters["category_id"],
           selectedFeedId: state.clusters.filters["feed_id"],

  };
}

const mapDispatchToProps = (dispatch) => ({
  toggleCatFolding(e, catId) {
    e.stopPropagation();
    dispatch(toggleFolding(catId));
  },
  listClusters(e, filters, isDesktop, isFolded, selectedCategoryId) {
    e.stopPropagation();
    // hide menu if in splitted mode and we're openning a un-opened category or feed
    if(!isDesktop && (filters.feedId || (filters.categoryId && isFolded))) {
      dispatch(toggleMenu(false));
    }
    // toggling folding of category on selection
    /*
    if(isFolded && filters.categoryId){
      dispatch(toggleFolding(filters.categoryId));
    } else if (!isFolded && filters.categoryId && filters.categoryId === selectedCategoryId) {
      dispatch(toggleFolding(filters.categoryId));
    }
    */
    dispatch(doListClusters(filters));
  },
});

function FeedRow({ index, style, feedListRows,
                   isFoldedFromParent, selectedCategoryId, selectedFeedId,
                   listClusters, toggleCatFolding }) {
  const classes = feedListStyle();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const obj = feedListRows[index];
  const isSelected = (selectedFeedId === obj.id && obj.type === "feed") || obj.id === selectedCategoryId;
  const badge = <Badge badgeContent={obj.unread} color="primary" className={classes.feedBadge}></Badge>;
  if (obj.type === "feed") {
    const icon = <FeedIcon iconUrl={obj["icon_url"]} />;
    return (
      <ListItem button
          key={`f${obj.id}-${isSelected ? "s" : ""}-${obj.unread}`}
          style={style}
          className={classes.feedItem}
          selected={isSelected}
          onClick={(e) => (listClusters(e, { feedId: obj.id }, isDesktop))}
        >
        {badge}
        {icon}
        <ListItemText primary={obj.str} className={classes.feedItemText}/>
      </ListItem>
    );
  }
  const isAllCateg = obj.type === "all-categ";
  let foldButton;
  if (!isAllCateg) {
    const FoldButton = obj.folded ? ExpandMore: ExpandLess;
    foldButton = <FoldButton className={classes.foldButton} onClick={(e) => (toggleCatFolding(e, obj.id))} />;
  }
  return (
    <ListItem button
        key={`c${obj.id}-${isSelected ? "s" : ""}-${obj.unread}`}
        style={style} selected={isSelected}
        onClick={(e) => (listClusters(e, { categoryId: isAllCateg ? "all" : obj.id}, isDesktop, obj.folded, selectedCategoryId ))}
        className={isAllCateg ? classes.catItemAll : classes.catItem}>
      {obj.unread && !isAllCateg ? badge : null}
      <ListItemText primary={isAllCateg ? "All" : obj.str} className={isAllCateg ? classes.catItemAllText : classes.catItemText} />
      {foldButton}
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
