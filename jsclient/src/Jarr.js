import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import CssBaseline from "@material-ui/core/CssBaseline";

import useStyles from "./Jarr.styles.js";
import Login from "./features/login/Login";
import TopMenu from "./features/topmenu/TopMenu";
import FeedList from "./features/feedlist/FeedList";
import EditPanel from "./features/editpanel/EditPanel";
import ClusterList from "./features/clusterlist/ClusterList";

function mapStateToProps(state) {
  return { isLogged: !!state.login.token, };
}

function Jarr({ isLogged, isLeftMenuOpen }) {
  const classes = useStyles();
  if (!isLogged) {
    return (
       <div className={classes.root}>
         <CssBaseline />
         <Login />;
       </div>
    );
  }
  return (
    <div className={classes.root}>
      <CssBaseline />
      <TopMenu />
      <FeedList />
      <ClusterList />
      <EditPanel />
   </div>
  );
}

Jarr.propTypes = {
  isLogged: PropTypes.bool.isRequired,
};

export default connect(mapStateToProps)(Jarr);
