import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import { TextField, Button, CircularProgress } from '@material-ui/core';
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
  return (
    <form className={styles.loginForm} noValidate autoComplete="off"
      onSubmit={onSubmit}>
      <TextField required id="jarr-login" label="Login"
        disabled={isLoading} error={isLoginError} helperText={loginError}
      />
      <TextField required id="jarr-password" label="Password" type="password"
        disabled={isLoading} error={isLoginError}
      />
      <Button variant="contained" type="submit">Login</Button>
      {isLoading ? <CircularProgress /> : undefined }
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
