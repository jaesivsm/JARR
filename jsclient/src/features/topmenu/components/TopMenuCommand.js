import React from "react";
import PropTypes from "prop-types";
import Tooltip from "@material-ui/core/Tooltip";
import MenuItem from "@material-ui/core/MenuItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import topMenuStyle from "../topMenuStyle";

function TopMenuCommand({ burgered, icon, className, title, onClick, setShowMenu }) {
  const classes = topMenuStyle();
  if (burgered) {
    return (
      <MenuItem onClick={() => {setShowMenu(false);onClick();}}>
        <ListItemIcon>
          <IconButton edge="start" color="inherit"
            className={classes.menuButton}>
            {icon}
          </IconButton>
        </ListItemIcon>
        <Typography>{title}</Typography>
      </MenuItem>
    );
  }
  return (
    <Tooltip title={title}>
      <IconButton color="inherit"
        onClick={onClick} className={className}
      >
        {icon}
      </IconButton>
    </Tooltip>
  );
}

TopMenuCommand.propTypes = {
  burgered: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  setShowMenu: PropTypes.func.isRequired,
};

export default TopMenuCommand;
