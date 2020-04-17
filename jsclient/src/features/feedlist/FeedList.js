import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// components
import Drawer from "@material-ui/core/Drawer";
import List from "@material-ui/core/List";
import IconButton from "@material-ui/core/IconButton";
// icons
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import AddFeedIcon  from "@material-ui/icons/Add";
import AddCategoryIcon from "@material-ui/icons/LibraryAdd";
import FoldAllCategoriesIcon from "@material-ui/icons/UnfoldLess";
import UnFoldAllCategoriesIcon from "@material-ui/icons/UnfoldMore";
// jarrs
import feedListStyle from "./feedListStyle";
import Category from "./Category";
import { doFetchFeeds, toggleFolding, toggleMenu } from "./feedSlice";
import { openPanel } from "../editpanel/editSlice";

function mapStateToProps(state) {
  return { categories: state.feeds.categories,
           selectedCategoryId: state.clusters.filters["category_id"],
           selectedFeedId: state.clusters.filters["feed_id"],
           isFoldedFromParent: state.feeds.isParentFolded,
           isOpen: state.feeds.isOpen && !state.edit.isOpen,
  };
}

const mapDispatchToProps = (dispatch) => ({
  fetchFeed() {
    return dispatch(doFetchFeeds());
  },
  toggleFeedList() {
    return dispatch(toggleMenu());
  },
  toggleAddPanel(objType) {
    return dispatch(openPanel({ objType }));
  },
  toggleFolder() {
    return dispatch(toggleFolding());
  },
});

function FeedList(props) {
  const classes = feedListStyle();
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      props.fetchFeed();
      setEverLoaded(true);
    }
  }, [everLoaded, props]);
  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={props.isOpen}
      className={classes.drawer}
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <div className={classes.drawerHeader}>
        <IconButton onClick={() => props.toggleAddPanel("feed")}>
          <AddFeedIcon />
        </IconButton>
        <IconButton onClick={() => props.toggleAddPanel("category")}>
          <AddCategoryIcon />
        </IconButton>
        <IconButton onClick={props.toggleFolder}>
         {props.isFoldedFromParent ? <UnFoldAllCategoriesIcon /> : <FoldAllCategoriesIcon />}
        </IconButton>
        <IconButton onClick={props.toggleFeedList}>
          <ChevronLeftIcon />
        </IconButton>
      </div>
      <List>
        {props.categories.map((category) => (
          <Category key={"cat-f" + props.isFoldedFromParent + "-" + category.id}
            id={category.id}
            name={category.name}
            feeds={category.feeds}
            isFoldedFromParent={props.isFoldedFromParent}
            selectedFeedId={props.selectedFeedId}
            selectedCategoryId={props.selectedCategoryId}
          />
        ))}
      </List>
    </Drawer>
  );
}

FeedList.propTypes = {
    categories: PropTypes.array.isRequired,
    isFoldedFromParent: PropTypes.bool.isRequired,
    isOpen: PropTypes.bool.isRequired,
    fetchFeed: PropTypes.func.isRequired,
    selectedFeedId: PropTypes.number,
    selectedCategoryId: PropTypes.number,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
