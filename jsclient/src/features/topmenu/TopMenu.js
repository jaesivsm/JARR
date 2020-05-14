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
import MoreVertIcon from "@material-ui/icons/MoreVert";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
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
import { toggleMenu } from "../feedlist/slice";
import { markedAllAsRead } from "../clusterlist/slice";
import doListClusters from "../../hooks/doListClusters";
import doFetchObjForEdit from "../../hooks/doFetchObjForEdit";
import doMarkAllAsRead from "../../hooks/doMarkAllAsRead";


function mapStateToProps(state) {
  return { isMenuButtonHidden: state.feeds.isOpen || state.edit.isOpen,
           isFilteringOnAll: state.clusters.filters.filter === "all",
           isFilteringOnLiked: state.clusters.filters.filter === "liked",
           isFeedListOpen: state.feeds.isOpen,
           isEditPanelOpen: state.edit.isOpen,
  };
}

const mapDispatchToProps = (dispatch) => ({
  filterClusters(filterValue) {
    dispatch(doListClusters({ filter: filterValue }));
  },
  markAllAsRead(onlySingles) {
    dispatch(doMarkAllAsRead(onlySingles));
    dispatch(markedAllAsRead({ onlySingles }));
  },
  toggleFeedList() {
    dispatch(toggleMenu(true));
  },
  openEditPanel() {
    dispatch(doFetchObjForEdit("user"));
  },
  logout() {
    dispatch(doLogout());
  },
});

function TopMenu(props) {
  const theme = useTheme();
  const classes = topMenuStyle();
  const burgered = !useMediaQuery(theme.breakpoints.up("md"));
  const isShifted = (props.isFeedListOpen === null ? !burgered : props.isFeedListOpen) && !props.isEditPanelOpen;

  // menu on smal display
  const [anchorEl, setAnchorEl] = useState(null);
  const showMenu = Boolean(anchorEl);
  const handleClick = (e) => setAnchorEl(e.currentTarget);

  // iter through commands on top menu
  const commandsDefs = {
    unread: { label: (!props.isFilteringOnAll
                      ? "Show all"
                      : "Show unread articles"),
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

  const commands = Object.entries(commandsDefs).map(([key, command]) => {
      if (burgered) {
        return (<MenuItem onClick={(e) => {
                    setAnchorEl(null);
                    command.onClick();
                }}
                  key={`command-${key}`}
                >
                  <ListItemIcon>
                    <IconButton edge="start" color="inherit"
                      className={classes.menuButton}>
                      {command.icon}
                    </IconButton>
                  </ListItemIcon>
                  <Typography>{command.label}</Typography>
                </MenuItem>);
      }
      return (<Tooltip title={command.label}
                key={`command-${key}`}
              >
                <IconButton color="inherit"
                  onClick={command.onClick} className={classes.menuButton}
                >
                  {command.icon}
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
         {showMenu ?  <MoreVertIcon /> : <MoreHorizIcon />}
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
          className={classes.burgeredMenu}
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
    [classes.appBarShift]: isShifted,
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
            <IconButton color="inherit" onClick={props.logout} className={classes.logoutButton}>
              <ExitToAppIcon />
            </IconButton>
          </Tooltip>
        </div>
      </Toolbar>
    </AppBar>
  );
}

TopMenu.propTypes = {
  isFeedListOpen: PropTypes.bool,
  isEditPanelOpen: PropTypes.bool.isRequired,
  isFilteringOnAll: PropTypes.bool.isRequired,
  isFilteringOnLiked: PropTypes.bool.isRequired,
  isMenuButtonHidden: PropTypes.bool.isRequired,
  toggleFeedList: PropTypes.func.isRequired,
  filterClusters: PropTypes.func.isRequired,
  markAllAsRead: PropTypes.func.isRequired,
  logout: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(TopMenu);
