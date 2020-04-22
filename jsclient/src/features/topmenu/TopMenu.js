import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import clsx from "clsx";
// material components
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
// material icons
import MenuIcon from "@material-ui/icons/Menu";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";
import MarkAllAsReadIcon from "@material-ui/icons/LibraryAddCheck";
import MarkALlNonClusterAsReadIcon from "@material-ui/icons/PlaylistAddCheck";
import FilterAllOrFavoriteIcon from "@material-ui/icons/StarBorder";
import FilterFavoriteIcon from "@material-ui/icons/Star";
import FilterAllIcon from "@material-ui/icons/IndeterminateCheckBox";
import FilterUnreadIcon from "@material-ui/icons/CheckBoxOutlineBlank";
import SettingsIcon from "@material-ui/icons/Settings";
// jarr
import topMenuStyle from "./topMenuStyle";
import { doLogout } from "../login/userSlice";
import { toggleMenu, doMarkAllAsRead } from "../feedlist/feedSlice";
import { doListClusters } from "../clusterlist/clusterSlice";
import { doFetchObjForEdit } from "../editpanel/editSlice";


function mapStateToProps(state) {
  return { isShifted: state.feeds.isOpen && !state.edit.isOpen,
           isMenuButtonHidden: state.feeds.isOpen || state.edit.isOpen,
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
  openEditPanel() {
    return dispatch(doFetchObjForEdit("user"));
  },
  logout() {
    return dispatch(doLogout());
  },
});

function TopMenu(props) {
  const classes = topMenuStyle();

  const className = clsx(classes.appBar, {
    [classes.appBarShift]: props.isShifted,
  });
  return (
    <AppBar position="fixed" className={className}>
      <Toolbar className={clsx(classes.toolbar)}>
        <div>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={props.toggleFeedList}
            edge="start"
            className={clsx(classes.menuButton, props.isMenuButtonHidden && classes.hide)}
          >
            <MenuIcon />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.filterClusters(props.isFilteringOnAll ? null : "all" )}
            className={clsx(classes.menuButton)}
          >
            {props.isFilteringOnAll ? <FilterAllIcon /> : <FilterUnreadIcon />}
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => props.filterClusters(props.isFilteringOnLiked ? null : "liked" )}
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
        <Typography>JARR</Typography>
        <div>
          <IconButton color="inherit" onClick={props.openEditPanel}>
            <SettingsIcon />
          </IconButton>
          <IconButton color="inherit" onClick={props.logout}>
            <ExitToAppIcon />
          </IconButton>
        </div>
      </Toolbar>
    </AppBar>
  );
}

TopMenu.propTypes = {
  isShifted: PropTypes.bool.isRequired,
  isFilteringOnAll: PropTypes.bool.isRequired,
  isFilteringOnLiked: PropTypes.bool.isRequired,
  isMenuButtonHidden: PropTypes.bool.isRequired,
  toggleFeedList: PropTypes.func.isRequired,
  filterClusters: PropTypes.func.isRequired,
  markAllAsRead: PropTypes.func.isRequired,
  logout: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(TopMenu);
