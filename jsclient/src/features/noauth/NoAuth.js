import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { Switch, Route } from "react-router-dom";
// material ui components
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import Divider from "@material-ui/core/Divider";
import CircularProgress from "@material-ui/core/CircularProgress";
import IconButton from "@material-ui/core/IconButton";
import Close from "@material-ui/icons/Close";
// jarr
import { doLogin, responseRecieved } from "./noAuthSlice";
import makeStyles from "./components/style";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import InitPasswordRecovery from "./components/InitPasswordRecovery";
import PasswordRecovery from "./components/PasswordRecovery";

function mapStateToProps(state) {
  return { isLoading: state.noauth.loading,
           noToken: (!state.noauth.loading
                     && !!state.auth.login
                     && !!state.auth.password
                     && !state.auth.token),
           savedLogin: state.auth.login,
           savedPassword: state.auth.password,
           recovery: (state.noauth.recovery ? state.noauth.recovery.statusText : ""),
  };
}

const mapDispatchToProps = (dispatch) => ({
  hiddenLogin (login, password) {
    return dispatch(doLogin(login, password));
  },
  clearStore() {
    return dispatch(responseRecieved());
  },
});

function NoAuth({ isLoading, noToken, savedLogin, savedPassword, recovery, hiddenLogin, clearStore }) {
  useEffect(() => {
    if (savedLogin && savedPassword && noToken) {
        hiddenLogin(savedLogin, savedPassword);
    }
  });
  const classes = makeStyles();
  const [formType, setFormType] = useState("login");
  const closeLoginSubPage = () => {
    setFormType("login");
    clearStore();
  };

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
      <>
        <Divider />
        <Grid item className={classes.loginButton}>
          <div>No account ?</div>
          <Button variant="contained" onClick={(e) => setFormType("signup")}>
            Sign up
          </Button>
        </Grid>
        <Divider />
        <Grid item className={classes.loginButton}>
          <div>Forgotten password ?</div>
          <Button variant="contained" onClick={(e) => setFormType("recover")}>
            Recover
          </Button>
        </Grid>
      </>
    );
  } else if (formType === "signup") {
    form = <SignUp isLoading={isLoading} />;
    header = (
      <Grid item className={classes.loginButton}>
         <IconButton onClick={closeLoginSubPage}>
           <Close />
         </IconButton>
         {isLoading ? <CircularProgress /> : <span>Sign Up !</span>}
       </Grid>
    );
  } else if (formType === "recover") {
    form = <InitPasswordRecovery />;
    header = (
      <Grid item className={classes.loginButton}>
         <IconButton onClick={closeLoginSubPage}>
           <Close />
         </IconButton>
         {isLoading ? <CircularProgress /> : <span>Password recovery</span>}
       </Grid>
    );
    if (recovery === "NO CONTENT") {
      footer = (
        <Grid item>
          An email has been sent to you, please follow instruction to
          complete recovery.
        </Grid>
      );

    } else if (recovery === "BAD REQUEST") {
      footer = (
        <Grid item>
          We could not generate you a recovery token, sorry !
        </Grid>
      );
    }
  }

  return (
    <Grid container className={classes.loginContainer} direction="column" >
      <Switch>
        <Route path="/recovery/:login/:email/:token">
          <PasswordRecovery />
          {recovery === "NOT FOUND" ? <Grid item>Could not find your user</Grid> : null}
          {recovery === "FORBIDDEN" ? <Grid item>Password NOT updated, token is expired. Please generate a new one.</Grid>: null}
        </Route>
        <Route path="/">
          {header}
          {form}
          {footer}
        </Route>
      </Switch>
    </Grid>
  );
}

NoAuth.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  noToken: PropTypes.bool.isRequired,
  savedLogin: PropTypes.string,
  savedPassword: PropTypes.string,
  recovery: PropTypes.string.isRequired,
  hiddenLogin: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(NoAuth);
