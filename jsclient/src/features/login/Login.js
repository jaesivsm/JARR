import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import { Grid, TextField, Button, CircularProgress } from '@material-ui/core';
import styles from './Login.module.css';
import { doLogin } from './loginSlice.js';

function mapStateToProps(state) {
    return { isLoading: state.login.loading,
             isLoginError: state.login.error !== undefined,
             loginError: state.login.error };
};

const mapDispatchToProps = (dispatch) => ({
    onSubmit (e) {
        e.preventDefault();
        const login = e.target.querySelector("input#jarr-login").value;
        const password = e.target.querySelector("input#jarr-password").value;
        return dispatch(doLogin(login, password));
    }
});

function Login({ isLoading, isLoginError, loginError, onSubmit }) {
  let info;
  if (isLoading) {
    info = <CircularProgress />;
  } else {
    info = <span>Welcome to JARR !</span>;
  }
  return (
    <form autoComplete="off" onSubmit={onSubmit}>
      <Grid container className={styles.loginContainer} spacing={4}>
        <Grid item xs={6}>
          <TextField required id="jarr-login" label="Login"
            className={styles.loginInput}
            disabled={isLoading} error={isLoginError} helperText={loginError}
          />
        </Grid>

        <Grid item xs={6}>
          {info}
        </Grid>
        <Grid item xs={6}>
          <TextField required id="jarr-password" label="Password" type="password"
            className={styles.loginInput}
            disabled={isLoading} error={isLoginError}
          />
        </Grid>
        <Grid item xs={6}>
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
    onSubmit: PropTypes.func.isRequired,
    loginError: PropTypes.string,
}

export default connect(mapStateToProps, mapDispatchToProps)(Login);
