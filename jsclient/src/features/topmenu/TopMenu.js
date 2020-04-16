import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import clsx from "clsx";

import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";
import MarkAllAsReadIcon from "@material-ui/icons/LibraryAddCheck";
import MarkALlNonClusterAsReadIcon from "@material-ui/icons/PlaylistAddCheck";
import FilterAllOrFavoriteIcon from '@material-ui/icons/StarBorder';
import FilterFavoriteIcon from "@material-ui/icons/Star";
import FilterAllIcon from '@material-ui/icons/IndeterminateCheckBox';
import FilterUnreadIcon from "@material-ui/icons/CheckBoxOutlineBlank";

import { doLogout } from "../login/userSlice";
import { toggleMenu } from "../feedlist/feedSlice";
import { doListClusters, doMarkAllAsRead } from "../clusterlist/clusterSlice";

function mapStateToProps(state) {
  return { isLeftMenuOpen: state.feeds.isOpen && !state.login.isRightPanelOpen,
           isMenuIconHidden: state.login.isLeftMenuOpen || state.login.isRightPanelOpen,
           isFilteringOnAll: state.clusters.filters.filter === "all",
           isFilteringOnLiked: state.clusters.filters.filter === "liked",
  };
}

const mapDispatchToProps = (dispatch) => ({
  filterClusters(filterValue) {
    return dispatch(doListClusters({ filter: filterValue }));
  },
  markAllAsRead(onlySingles) {
    return dispatch(doMarkAllAsRead(onlySingles));
  },
  toggleFeedList() {
    return dispatch(toggleMenu());
  },
  logout() {
    return dispatch(doLogout());
  },
});

function TopMenu(props) {
  return (
    <AppBar position="fixed"
        className={clsx(props.classes.appBar, {
          [props.classes.appBarShift]: props.isLeftMenuOpen,
      })}>
      <Toolbar className={clsx(props.classes.toolbar)}>
        <div>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={props.toggleFeedList}
            edge="start"
            className={clsx(props.classes.menuButton, props.isMenuIconHidden && props.classes.hide)}
          >
            <MenuIcon />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.filterClusters(props.isFilteringOnAll ? null : 'all' )}
            className={clsx(props.classes.menuButton)}
          >
            {props.isFilteringOnAll ? <FilterAllIcon /> : <FilterUnreadIcon />}
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.filterClusters(props.isFilteringOnLiked ? null : 'liked' )}
            className={clsx(props.classes.menuButton)}
          >
            {props.isFilteringOnLiked ? <FilterFavoriteIcon /> : <FilterAllOrFavoriteIcon />}
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.markAllAsRead(false)}
            className={clsx(props.classes.menuButton)}
          >
            <MarkAllAsReadIcon />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.markAllAsRead(true)}
            className={clsx(props.classes.menuButton)}
          >
            <MarkALlNonClusterAsReadIcon />
          </IconButton>
        </div>
        <div>
          <IconButton
            color="inherit"
            onClick={props.logout}
            className={clsx(props.classes.menuCommand)}
          >
            <ExitToAppIcon />
          </IconButton>
        </div>
      </Toolbar>
    </AppBar>
  );
}

TopMenu.propTypes = {
  isLeftMenuOpen: PropTypes.bool.isRequired,
  isMenuIconHidden: PropTypes.bool.isRequired,
  isFilteringOnAll: PropTypes.bool.isRequired,
  isFilteringOnLiked: PropTypes.bool.isRequired,
  toggleFeedList: PropTypes.func.isRequired,
  filterClusters: PropTypes.func.isRequired,
  markAllAsRead: PropTypes.func.isRequired,
  logout: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(TopMenu);
