import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import clsx from "clsx";

import CssBaseline from "@material-ui/core/CssBaseline";

import useStyles from "./Jarr.styles.js";
import Login from "./features/login/Login";
import TopMenu from "./features/topmenu/TopMenu";
import FeedList from "./features/feedlist/FeedList";
import EditPanel from "./features/editpanel/EditPanel";
import ClusterList from "./features/clusterlist/ClusterList";

function mapStateToProps(state) {
  return { isLogged: !!state.login.token,
           isLeftMenuOpen: state.feeds.isOpen && !state.login.isRightPanelOpen,
  };
}

function Jarr({ isLogged, isLeftMenuOpen }) {
  const classes = useStyles();
  if (!isLogged) {
    return <Login />;
  }
  return (
    <div className={classes.root}>
      <CssBaseline />
      <TopMenu classes={classes} />
      <FeedList classes={classes} />
      <ClusterList
        className={clsx(classes.content, {
          [classes.contentShift]: isLeftMenuOpen,
        })}
      />
      <EditPanel classes={classes} />
   </div>
  );
}

Jarr.propTypes = {
  isLogged: PropTypes.bool.isRequired,
  isLeftMenuOpen: PropTypes.bool.isRequired,
};

export default connect(mapStateToProps)(Jarr);
