import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { useNavigate } from "react-router-dom";
// material ui component
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import Badge from "@mui/material/Badge";
import ListItemText from "@mui/material/ListItemText";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
// jarr
import doListClusters from "../../hooks/doListClusters";
import { toggleMenu, toggleFolding, createFeedListFilter } from "./slice";
import useStyles from "./feedListStyle";
import FeedIcon from "../../components/FeedIcon";

function mapStateToProps(state) {
  const feedListFilter = createFeedListFilter(state.feeds.feedSearchString);
  return { feedListRows: state.feeds.feedListRows.filter(feedListFilter),
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
  toggleMenuFunc() {
    dispatch(toggleMenu(false));
  },
  listClusters(filters) {
    dispatch(doListClusters(filters));
  },
});

function FeedRow({ index, style, feedListRows,
                   isFoldedFromParent, selectedCategoryId, selectedFeedId,
                   toggleCatFolding, toggleMenuFunc, listClusters }) {
  const theme = useTheme();
  const classes = useStyles();
  const navigate = useNavigate();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const obj = feedListRows[index];
  const isSelected = (selectedFeedId === obj.id && obj.type === "feed") || obj.id === selectedCategoryId;
  const badge = <Badge badgeContent={obj.unread} color="primary" className={classes.feedBadge}></Badge>;
  if (obj.type === "feed") {
    const icon = <FeedIcon iconUrl={obj["icon_url"]} />;
    return (
      <ListItem
          key={`f${obj.id}-${isSelected ? "s" : ""}-${obj.unread}`}
          style={style}
          disablePadding
        >
        <ListItemButton
          className={classes.feedItem}
          selected={isSelected}
          onClick={(e) => {
            e.stopPropagation();
            if(!isDesktop) {
              toggleMenuFunc();
            }
            listClusters({ feedId: obj.id });
            navigate(`/feed/${obj.id}`);
          }}
        >
          {badge}
          {icon}
          <ListItemText primary={obj.str} className={classes.feedItemText}/>
        </ListItemButton>
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
    <ListItem
        key={`c${obj.id}-${isSelected ? "s" : ""}-${obj.unread}`}
        style={style}
        disablePadding
      >
      <ListItemButton
        selected={isSelected}
        onClick={(ev) => {
          ev.stopPropagation();
          if(!isDesktop && obj.folded) {
            toggleMenuFunc();
          }
          if(obj.folded && !isAllCateg){
            toggleCatFolding(ev, obj.id);
          } else if (!obj.folded && !isAllCateg && obj.id === selectedCategoryId) {
            toggleCatFolding(ev, obj.id);
          }
          listClusters({ categoryId: isAllCateg ? "all" : obj.id });
          navigate(`/category/${isAllCateg ? "all" : obj.id}`);
        }}
        className={isAllCateg ? classes.catItemAll : classes.catItem}
      >
        {obj.unread && !isAllCateg ? badge : null}
        <ListItemText
          primary={isAllCateg ? "All" : obj.str}
          className={isAllCateg ? classes.catItemAllText : classes.catItemText}
        />
        {foldButton}
      </ListItemButton>
    </ListItem>
  );
}

FeedRow.propTypes = {
  index: PropTypes.number.isRequired,
  feedListRows: PropTypes.array.isRequired,
  selectedCategoryId: PropTypes.number,
  selectedFeedId: PropTypes.number,
  toggleCatFolding: PropTypes.func.isRequired,
  toggleMenuFunc: PropTypes.func.isRequired,
  listClusters: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedRow);
