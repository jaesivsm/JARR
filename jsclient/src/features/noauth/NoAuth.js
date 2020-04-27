import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import CircularProgress from "@material-ui/core/CircularProgress";
import IconButton from "@material-ui/core/IconButton";
import Close from "@material-ui/icons/Close";
// jarr
import { doLogin } from "./noAuthSlice";
import makeStyles from "./components/style";
import Login from "./components/Login";
import SignUp from "./components/SignUp";

function mapStateToProps(state) {
    return { isLoading: state.noauth.loading,
             noToken: (!state.noauth.loading
                       && !!state.auth.login
                       && !!state.auth.password
                       && !state.auth.token),
             savedLogin: state.auth.login,
             savedPassword: state.auth.password,
             };
}

const mapDispatchToProps = (dispatch) => ({
  hiddenLogin (login, password) {
    return dispatch(doLogin(login, password));
  },
});

function NoAuth({ isLoading, noToken, savedLogin, savedPassword, hiddenLogin }) {
  useEffect(() => {
    if (savedLogin && savedPassword && noToken) {
        hiddenLogin(savedLogin, savedPassword);
    }
  });
  const classes = makeStyles();
  const [formType, setFormType] = useState("login");

  let form;
  let header;
  let footer;
  if (formType === "login") {
    if (isLoading) {
      header = <Grid item><CircularProgress /></Grid>;
    } else {
      header = <Grid item><span>Welcome to JARR !</span></Grid>;
    }
    form = <Login isLoading={isLoading} />;
    footer = (
      <Grid item className={classes.loginButton}>
        <Button variant="contained" onClick={(e) => setFormType("signup")}>
          Sign up
        </Button>
      </Grid>
    );
  } else if (formType === "signup") {
    form = <SignUp isLoading={isLoading} />;
    header = (
      <Grid item className={classes.loginButton}>
         <IconButton onClick={() => setFormType("login")}>
           <Close />
         </IconButton>
         {isLoading ? <CircularProgress /> : <span>Sign Up !</span>}
       </Grid>
    );
  }

  return (
    <Grid container className={classes.loginContainer} direction="column" >
      {header}
      {form}
      {footer}
    </Grid>
  );
}

NoAuth.propTypes = {
    isLoading: PropTypes.bool.isRequired,
    savedLogin: PropTypes.string,
    savedPassword: PropTypes.string,
    noToken: PropTypes.bool.isRequired,
    hiddenLogin: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(NoAuth);
