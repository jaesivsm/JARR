import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import clsx from "clsx";

import Drawer from "@material-ui/core/Drawer";
import CssBaseline from "@material-ui/core/CssBaseline";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import AddFeedIcon  from "@material-ui/icons/Add";
import AddCategoryIcon from "@material-ui/icons/LibraryAdd";
import FoldAllCategoriesIcon from "@material-ui/icons/UnfoldLess";
import UnFoldAllCategoriesIcon from "@material-ui/icons/UnfoldMore";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";
import MarkAllAsReadIcon from "@material-ui/icons/LibraryAddCheck";
import MarkALlNonClusterAsReadIcon from "@material-ui/icons/PlaylistAddCheck";
import FilterAllOrFavoriteIcon from '@material-ui/icons/StarBorder';
import FilterFavoriteIcon from "@material-ui/icons/Star";
import FilterAllIcon from '@material-ui/icons/IndeterminateCheckBox';
import FilterUnreadIcon from "@material-ui/icons/CheckBoxOutlineBlank";

import useStyles from "./Jarr.styles.js";
import Login from "./features/login/Login";
import FeedList from "./features/feedlist/FeedList";
import ClusterList from "./features/clusterlist/ClusterList";
import { toggleLeftMenu, toggleFolding, doLogout } from "./features/login/userSlice.js";
import { doListClusters, doMarkAllAsRead } from "./features/clusterlist/clusterSlice";

function mapStateToProps(state) {
  return { isLogged: !!state.login.token,
           isLeftMenuOpen: state.login.isLeftMenuOpen,
           isLeftMenuFolded: state.login.isLeftMenuFolded,
           currentFilter: state.clusters.filters.filter,
           isFilteringOnAll: state.clusters.filters.filter === 'all',
           isFilteringOnLiked: state.clusters.filters.filter === 'liked',
  };
}

const mapDispatchToProps = (dispatch) => ({
  toggleDrawer() {
    return dispatch(toggleLeftMenu());
  },
  toggleFolder() {
    return dispatch(toggleFolding());
  },
  filterClusters(filterValue) {
    return dispatch(doListClusters({ filter: filterValue }));
  },
  markAllAsRead(onlySingles) {
    return dispatch(doMarkAllAsRead(onlySingles));
  },
  logout() {
    return dispatch(doLogout());
  },
});


function Jarr(props) {
  const classes = useStyles();
  if (!props.isLogged) {
    return <Login />;
  }
  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="fixed"
          className={clsx(classes.appBar, {
            [classes.appBarShift]: props.isLeftMenuOpen,
        })}>
        <Toolbar className={clsx(classes.toolbar)}>
          <div>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={props.toggleDrawer}
              edge="start"
              className={clsx(classes.menuButton, props.isLeftMenuOpen && classes.hide)}
            >
              <MenuIcon />
            </IconButton>
            <IconButton
              color="inherit"
              onClick={() => props.filterClusters(props.isFilteringOnAll ? null : 'all' )}
              className={clsx(classes.menuButton)}
            >
              {props.isFilteringOnAll ? <FilterAllIcon /> : <FilterUnreadIcon />}
            </IconButton>
            <IconButton
              color="inherit"
              onClick={() => props.filterClusters(props.isFilteringOnLiked ? null : 'liked' )}
              className={clsx(classes.menuButton)}
            >
              {props.isFilteringOnLiked ? <FilterFavoriteIcon /> : <FilterAllOrFavoriteIcon />}
            </IconButton>
            <IconButton
              color="inherit"
              onClick={() => props.markAllAsRead(false)}
              className={clsx(classes.menuButton)}
            >
              <MarkAllAsReadIcon />
            </IconButton>
            <IconButton
              color="inherit"
              onClick={() => props.markAllAsRead(true)}
              className={clsx(classes.menuButton)}
            >
              <MarkALlNonClusterAsReadIcon />
            </IconButton>
          </div>
          <div>
            <IconButton
              color="inherit"
              onClick={props.logout}
              className={clsx(classes.menuCommand)}
            >
              <ExitToAppIcon />
            </IconButton>
          </div>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="persistent"
        anchor="left"
        open={props.isLeftMenuOpen}
        className={classes.drawer}
        classes={{
          paper: classes.drawerPaper,
        }}
      >
        <div className={classes.drawerHeader}>
          <IconButton>
            <AddFeedIcon />
          </IconButton>
          <IconButton>
            <AddCategoryIcon />
          </IconButton>
          <IconButton onClick={props.toggleFolder}>
           {props.isLeftMenuFolded ? <UnFoldAllCategoriesIcon /> : <FoldAllCategoriesIcon />}
          </IconButton>
          <IconButton onClick={props.toggleDrawer}>
            <ChevronLeftIcon />
          </IconButton>
        </div>
        <FeedList />
      </Drawer>
      <ClusterList
        className={clsx(classes.content, {
          [classes.contentShift]: props.isLeftMenuOpen,
        })}
      />
   </div>
  );
}

Jarr.propTypes = {
  isLogged: PropTypes.bool.isRequired,
  isLeftMenuOpen: PropTypes.bool.isRequired,
  isLeftMenuFolded: PropTypes.bool.isRequired,
  isFilteringOnAll: PropTypes.bool.isRequired,
  isFilteringOnLiked: PropTypes.bool.isRequired,
  toggleDrawer: PropTypes.func.isRequired,
  toggleFolder: PropTypes.func.isRequired,
  filterClusters: PropTypes.func.isRequired,
  markAllAsRead: PropTypes.func.isRequired,
  logout: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(Jarr);
