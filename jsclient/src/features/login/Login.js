import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import { TextField, Button, CircularProgress } from '@material-ui/core';
import styles from './Login.module.css';
import { login } from './loginSlice.js';

function mapStateToProps(state) {
    return { isLoading: state.login.loading };
};

const mapDispatchToProps = (dispatch) => ({
    onSubmit (e) {
        e.preventDefault();
        const payload = { login: e.target.querySelector("input#jarr-login").value,
                          password: e.target.querySelector("input#jarr-password").value };
        return dispatch(login(payload));
    }
});

function Login({ isLoading, onSubmit }) {
  return (
    <form className={styles.loginForm} noValidate autoComplete="off"
      onSubmit={onSubmit}>
      <TextField disabled={isLoading} required id="jarr-login" label="Login" />
      <TextField disabled={isLoading} required id="jarr-password" label="Password" type="password" />
      <Button variant="contained" type="submit">Login</Button>
      {isLoading ? <CircularProgress /> : undefined }
    </form>
  );
}

Login.propTypes = {
    isLoading: PropTypes.bool.isRequired,
    onSubmit: PropTypes.func.isRequired
}

export default connect(mapStateToProps, mapDispatchToProps)(Login);
