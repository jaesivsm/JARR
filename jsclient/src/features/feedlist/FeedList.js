import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// components
import { FixedSizeList } from "react-window";
import Drawer from "@material-ui/core/Drawer";
import InputBase from "@material-ui/core/InputBase";
import IconButton from "@material-ui/core/IconButton";
// icons
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import AddFeedIcon  from "@material-ui/icons/Add";
import AddCategoryIcon from "@material-ui/icons/LibraryAdd";
import FoldAllCategoriesIcon from "@material-ui/icons/UnfoldLess";
import UnFoldAllCategoriesIcon from "@material-ui/icons/UnfoldMore";
import SearchIcon from "@material-ui/icons/Search";
import Divider from "@material-ui/core/Divider";
import Close from "@material-ui/icons/Close";
// jarrs
import feedListStyle from "./feedListStyle";
import FeedRow from "./FeedRow";
import { doFetchFeeds, doFetchUnreadCount, toggleAllFolding, toggleMenu,
         setSearchFilter,
} from "./feedSlice";
import { openPanel } from "../editpanel/editSlice";
import { feedListWidth } from "../../const";

function mapStateToProps(state) {
  return { itemCount: state.feeds.feedListRows.filter(state.feeds.feedListFilter).length,
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
  setSearchFilter(searchStr) {
    return dispatch(setSearchFilter(searchStr));
  },
});

function FeedList(props) {
  const classes = feedListStyle();
  const [everLoaded, setEverLoaded] = useState(false);
  const [displaySearch, setDisplaySearch] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      props.fetchFeed();
      props.fetchUnreadCount();
      setEverLoaded(true);
    }
  }, [everLoaded, props]);
  let searchBar;
  if (displaySearch) {
    searchBar = (
      <div className={classes.drawerHeader}>
        <InputBase placeholder="Search feed…" onChange={(e) => props.setSearchFilter(e.target.value)} />
        <IconButton onClick={() => {props.setSearchFilter(null); setDisplaySearch(false)}}>
          <Close />
        </IconButton>
      </div>
    );
  }
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
          <IconButton onClick={() => {
            if(displaySearch) { props.setSearchFilter(null); }
            setDisplaySearch(!displaySearch);
          }}>
            <SearchIcon />
          </IconButton>
        </div>
        <div>
          <IconButton onClick={props.toggleFeedList}>
            <ChevronLeftIcon />
          </IconButton>
        </div>
      </div>
      {displaySearch ? <Divider /> : null }
      {searchBar}
      <Divider />
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
    selectedFeedId: PropTypes.number,
    selectedCategoryId: PropTypes.number,
    fetchFeed: PropTypes.func.isRequired,
    fetchUnreadCount: PropTypes.func.isRequired,
    toggleFeedList: PropTypes.func.isRequired,
    toggleAddPanel: PropTypes.func.isRequired,
    setSearchFilter: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
