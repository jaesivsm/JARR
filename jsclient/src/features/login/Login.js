import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import { Grid, TextField, Button, CircularProgress } from '@material-ui/core';
import styles from './Login.module.css';
import { doLogin } from './userSlice.js';

function mapStateToProps(state) {
    return { isLoading: state.login.loading,
             isLoginError: state.login.error !== undefined,
             noToken: !state.login.loading && state.login.login && state.login.password && !state.login.token,
             savedLogin: state.login.login,
             savedPassword: state.login.password,
             loginError: state.login.error };
};

const mapDispatchToProps = (dispatch) => ({
  onSubmit (e) {
    e.preventDefault();
    const login = e.target.querySelector("input#jarr-login").value;
    const password = e.target.querySelector("input#jarr-password").value;
    return dispatch(doLogin(login, password));
  },
  hiddenLogin (login, password) {
    return dispatch(doLogin(login, password));
  },
});

function Login({ isLoading, isLoginError, noToken, savedLogin, savedPassword, loginError, onSubmit, hiddenLogin }) {
  useEffect(() => {
    if (savedLogin && savedPassword && noToken) {
        hiddenLogin(savedLogin, savedPassword);
    }
  });
  let info;
  if (isLoading) {
    info = <CircularProgress />;
  } else {
    info = <span>Welcome to JARR !</span>;
  }
  return (
    <form autoComplete="off" onSubmit={onSubmit}>
      <Grid container className={styles.loginContainer} spacing={4} justify="center" direction="column" alignItems="center">
        <Grid>{info}</Grid>
        <Grid item>
          <TextField required id="jarr-login" label="Login"
            className={styles.loginInput}
            disabled={isLoading} error={isLoginError} helperText={loginError}
          />
        </Grid>
        <Grid item>
          <TextField required id="jarr-password" label="Password" type="password"
            className={styles.loginInput}
            disabled={isLoading} error={isLoginError}
          />
        </Grid>
        <Grid item>
          <Button align="right" variant="contained" type="submit">
            Login
          </Button>
        </Grid>
      </Grid>
    </form>
  );
}

Login.propTypes = {
    isLoading: PropTypes.bool.isRequired,
    isLoginError: PropTypes.bool.isRequired,
    savedLogin: PropTypes.string,
    savedPassword: PropTypes.string,
    noToken: PropTypes.bool.isRequired,
    onSubmit: PropTypes.func.isRequired,
    hiddenLogin: PropTypes.func.isRequired,
    loginError: PropTypes.string,
}

export default connect(mapStateToProps, mapDispatchToProps)(Login);
