import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import { TextField, Button } from '@material-ui/core';
import styles from './Login.module.css';
import { login } from './loginSlice.js';

const mapDispatchToProps = (dispatch) => ({
    onSubmit (e) {
        e.preventDefault();
        const payload = { login: e.target.querySelector("input#jarr-login").value,
                          password: e.target.querySelector("input#jarr-password").value };
        return dispatch(login(payload));
    }
});

function Login({ onSubmit }) {
  return (
    <form className={styles.loginForm} noValidate autoComplete="off"
      onSubmit={onSubmit}>
      <TextField required id="jarr-login" label="Login" />
      <TextField required id="jarr-password" label="Password" type="password" />
      <Button variant="contained" type="submit">Login</Button>
    </form>
  );
}

Login.propTypes = {
    onSubmit: PropTypes.func.isRequired
}

export default connect(null, mapDispatchToProps)(Login);
