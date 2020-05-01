import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import clsx from "clsx";
// material components
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Tooltip from "@material-ui/core/Tooltip";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
// material icons
import MenuIcon from "@material-ui/icons/Menu";
import MenuOpenIcon from '@material-ui/icons/MenuOpen';
import FilterAllOrFavoriteIcon from "@material-ui/icons/StarBorder";
import FilterFavoriteIcon from "@material-ui/icons/Star";
import FilterAllIcon from "@material-ui/icons/IndeterminateCheckBox";
import FilterUnreadIcon from "@material-ui/icons/CheckBoxOutlineBlank";
import MarkAllAsReadIcon from "@material-ui/icons/LibraryAddCheck";
import MarkAllNonClusterAsReadIcon from "@material-ui/icons/PlaylistAddCheck";
import SettingsIcon from "@material-ui/icons/Settings";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";
// jarr
import topMenuStyle from "./topMenuStyle";
import { doLogout } from "../../authSlice";
import { toggleMenu, doMarkAllAsRead } from "../feedlist/feedSlice";
import { doListClusters, markedAllAsRead } from "../clusterlist/clusterSlice";
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
    dispatch(doMarkAllAsRead(onlySingles));
    return dispatch(markedAllAsRead());
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
  const theme = useTheme();
  const classes = topMenuStyle();
  const burgered = !useMediaQuery(theme.breakpoints.up("md"));

  // menu on smal display
  const [anchorEl, setAnchorEl] = useState(null);
  const showMenu = Boolean(anchorEl);
  const handleClick = (e) => setAnchorEl(e.currentTarget);

  // iter through commands on top menu
  const commandsDefs = {
    unread: { label: (!props.isFilteringOnAll
                      ? "Show unread articles"
                      : "Show all"),
              onClick: () => props.filterClusters(props.isFilteringOnAll
                                                  ? null : "all"),
              icon: (!props.isFilteringOnAll
                     ? <FilterUnreadIcon />
                     : <FilterAllIcon />)},
    liked: { label: (props.isFilteringOnLiked
                     ? "Show all"
                     : "Show liked articles"),
             onClick: () => props.filterClusters(props.isFilteringOnLiked
                                                 ? null : "liked" ),
             icon: (props.isFilteringOnLiked
                    ? <FilterFavoriteIcon />
                    : <FilterAllOrFavoriteIcon />
             ), },
    mark: { label: "Mark all as read",
            onClick: () => props.markAllAsRead(false),
            icon: <MarkAllAsReadIcon /> },
    markNC: { label: "Mark all non cluster as read",
              onClick: () => props.markAllAsRead(true),
              icon: <MarkAllNonClusterAsReadIcon /> },
  };

  const commands = Object.keys(commandsDefs).map((key) => {
      if (burgered) {
        return (<MenuItem onClick={(e) => {
                    setAnchorEl(null);
                    commandsDefs[key].onClick();
                }}
                  key={"command-" + key}
                >
                  <ListItemIcon>
                    <IconButton edge="start" color="inherit"
                      className={classes.menuButton}>
                      {commandsDefs[key].icon}
                    </IconButton>
                  </ListItemIcon>
                  <Typography>{commandsDefs[key].label}</Typography>
                </MenuItem>);
      }
      return (<Tooltip title={commandsDefs[key].label}
                key={"command" + key}
              >
                <IconButton color="inherit"
                  onClick={commandsDefs[key].onClick} className={classes.menuButton}
                >
                  {commandsDefs[key].icon}
                </IconButton>
              </Tooltip>);
    }
  );

  const showFeedList = (
    <Tooltip title="Show feed list">
      <IconButton
        color="inherit"
        aria-label="open drawer"
        onClick={props.toggleFeedList}
        edge="start"
        className={clsx(classes.menuButton,
                        props.isMenuButtonHidden && classes.hide)}>
        <MenuIcon />
      </IconButton>
    </Tooltip>
  );

  let menu;  // constructing menu depending on the display size
  if (burgered) {
    const openMenuIcon = (<IconButton
          color="inherit"
          onClick={handleClick}
        >
          <MenuOpenIcon />
        </IconButton>);

    menu = (
      <div>
        {showFeedList}
        {openMenuIcon}
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={showMenu}
          onClose={() => setAnchorEl(null)}
        >
          {commands}
        </Menu>
      </div>
    );
  } else {
    menu = (
      <div>
        {showFeedList}
        {commands}
      </div>
    );
  }

  const className = clsx(classes.appBar, {
    [classes.appBarShift]: props.isShifted,
  });
  return (
    <AppBar position="fixed" className={className}>
      <Toolbar className={clsx(classes.toolbar)}>
        {menu}
        <Typography>JARR</Typography>
        <div>
          <Tooltip title="Settings">
            <IconButton color="inherit" onClick={props.openEditPanel}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Logout">
            <IconButton color="inherit" onClick={props.logout}>
              <ExitToAppIcon />
            </IconButton>
          </Tooltip>
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
