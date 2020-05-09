import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// components
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { FixedSizeList } from "react-window";
import Drawer from "@material-ui/core/Drawer";
import InputBase from "@material-ui/core/InputBase";
import IconButton from "@material-ui/core/IconButton";
import Tooltip from "@material-ui/core/Tooltip";
import CircularProgress from "@material-ui/core/CircularProgress";
// icons
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import AddFeedIcon  from "@material-ui/icons/Add";
import AddCategoryIcon from "@material-ui/icons/LibraryAdd";
import FoldAllCategoriesIcon from "@material-ui/icons/UnfoldLess";
import UnFoldAllCategoriesIcon from "@material-ui/icons/UnfoldMore";
import SearchIcon from "@material-ui/icons/Search";
import Divider from "@material-ui/core/Divider";
import Close from "@material-ui/icons/Close";
import Alert from "@material-ui/lab/Alert";
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
           isFeedListOpen: state.feeds.isOpen,
           isEditPanelOpen: state.edit.isOpen,
           isLoading: state.feeds.loadingFeeds,
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
    return dispatch(toggleMenu(false));
  },
  toggleAddPanel(objType) {
    return dispatch(openPanel({ objType, isLoading: false }));
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
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const isOpen = (props.isFeedListOpen === null ? isDesktop : props.isFeedListOpen) && !props.isEditPanelOpen;
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
        <InputBase placeholder="Search feed…" autoFocus
          onChange={(e) => props.setSearchFilter(e.target.value)} />
        <IconButton onClick={() => {props.setSearchFilter(null); setDisplaySearch(false);} }>
          <Close />
        </IconButton>
      </div>
    );
  }

  const addFeedButton = (
    <IconButton onClick={() => props.toggleAddPanel("feed")}>
      <AddFeedIcon />
    </IconButton>);
  const addCategoryButton = (
    <IconButton onClick={() => props.toggleAddPanel("category")}>
      <AddCategoryIcon />
    </IconButton>);
  let list;
  if (props.isLoading) {
    list = <div className={classes.loadFeedList}><CircularProgress /></div>;
  } else if (props.itemCount === 1 && !displaySearch) {
    list = (
      <Alert severity="info" className={classes.welcome}>
        <p>Hello ! You seem to be new here, welcome !</p>
        <p>JARR is a tool to aggregate news feed. Since you don't have any feed, there is nothing to display yet.</p>
        <p>Click on {addFeedButton} here or at the top of this menu to add a new feed.</p>
        <p>JARR particularity is to allow clustering articles from various feeds to a condensed clusters. This allows a more dense and interesting news feed. You can of course control clustering settings from different level (user, category, and feed).</p>
        <p>You may later want to organize your feeds into categories, to do that add category by clicking on {addCategoryButton}.</p>
      </Alert>
    );
  } else {
    list = (
      <FixedSizeList height={1000} width={isDesktop ? feedListWidth-1 : '100%'} itemCount={props.itemCount} itemSize={34}>
        {FeedRow}
      </FixedSizeList>
    );
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={isOpen}
      className={classes.drawer}
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <div className={classes.drawerHeader}>
        <div>
          <Tooltip title="Add new feed">{addFeedButton}</Tooltip>
          <Tooltip title="Add new category">{addCategoryButton}</Tooltip>
          <Tooltip title={props.isFoldedFromParent ? "Unfold categories" : "Fold categories"}>
            <IconButton onClick={props.toggleFolder}>
             {props.isFoldedFromParent ? <UnFoldAllCategoriesIcon /> : <FoldAllCategoriesIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Search through feed list">
            <IconButton onClick={() => {
              if(displaySearch) { props.setSearchFilter(null); }
              setDisplaySearch(!displaySearch);
            }}>
              <SearchIcon />
            </IconButton>
          </Tooltip>
        </div>
        <div>
          <Tooltip title="Hide feed list">
            <IconButton onClick={props.toggleFeedList}>
              <ChevronLeftIcon />
            </IconButton>
          </Tooltip>
        </div>
      </div>
      {displaySearch ? <Divider /> : null }
      {searchBar}
      <Divider />
      {list}
    </Drawer>
  );
}

FeedList.propTypes = {
    itemCount: PropTypes.number.isRequired,
    isFoldedFromParent: PropTypes.bool.isRequired,
    isFeedListOpen: PropTypes.bool,
    isEditPanelOpen: PropTypes.bool.isRequired,
    isLoading: PropTypes.bool.isRequired,
    selectedFeedId: PropTypes.number,
    selectedCategoryId: PropTypes.number,
    fetchFeed: PropTypes.func.isRequired,
    fetchUnreadCount: PropTypes.func.isRequired,
    toggleFeedList: PropTypes.func.isRequired,
    toggleAddPanel: PropTypes.func.isRequired,
    setSearchFilter: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FeedList);
