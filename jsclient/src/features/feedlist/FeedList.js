import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// components
import Drawer from "@material-ui/core/Drawer";
import IconButton from "@material-ui/core/IconButton";
// icons
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import AddFeedIcon  from "@material-ui/icons/Add";
import AddCategoryIcon from "@material-ui/icons/LibraryAdd";
import FoldAllCategoriesIcon from "@material-ui/icons/UnfoldLess";
import UnFoldAllCategoriesIcon from "@material-ui/icons/UnfoldMore";
import { FixedSizeList } from "react-window";
// jarrs
import feedListStyle from "./feedListStyle";
import FeedRow from "./FeedRow";
import { doFetchFeeds, doFetchUnreadCount, toggleAllFolding, toggleMenu
} from "./feedSlice";
import { openPanel } from "../editpanel/editSlice";
import { feedListWidth } from "../../const";

function mapStateToProps(state) {
  return { itemCount: state.feeds.feedListRows.filter((row) => (!row.folded || row.type === "categ" || row.type === "all-categ")).length,
           isFoldedFromParent: state.feeds.isParentFolded,
           isOpen: state.feeds.isOpen && !state.edit.isOpen,
  };
}

const mapDispatchToProps = (dispatch) => ({
  fetchFeed() {
    return dispatch(doFetchFeeds());
  },
  fetchUnreadCount() {
    return dispatch(doFetchUnreadCount());
  },
  toggleFeedList() {
    return dispatch(toggleMenu());
  },
  toggleAddPanel(objType) {
    return dispatch(openPanel({ objType }));
  },
  toggleFolder() {
    return dispatch(toggleAllFolding());
  },
});

function FeedList(props) {
  const classes = feedListStyle();
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      props.fetchFeed();
      props.fetchUnreadCount();
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
        <div>
          <IconButton onClick={() => props.toggleAddPanel("feed")}>
            <AddFeedIcon />
          </IconButton>
          <IconButton onClick={() => props.toggleAddPanel("category")}>
            <AddCategoryIcon />
          </IconButton>
          <IconButton onClick={props.toggleFolder}>
           {props.isFoldedFromParent ? <UnFoldAllCategoriesIcon /> : <FoldAllCategoriesIcon />}
          </IconButton>
        </div>
        <div>
          <IconButton onClick={props.toggleFeedList}>
            <ChevronLeftIcon />
          </IconButton>
        </div>
      </div>
      <FixedSizeList height={1000} width={feedListWidth-1} itemCount={props.itemCount} itemSize={34}>
        {FeedRow}
      </FixedSizeList>
    </Drawer>
  );
}

FeedList.propTypes = {
    itemCount: PropTypes.number.isRequired,
    isFoldedFromParent: PropTypes.bool.isRequired,
    isOpen: PropTypes.bool.isRequired,
    fetchFeed: PropTypes.func.isRequired,
    selectedFeedId: PropTypes.number,
    selectedCategoryId: PropTypes.number,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
