import React from 'react';
import { useDispatch } from 'react-redux';
import { TextField, Button } from '@material-ui/core';
import styles from './Login.module.css';
import { login } from './loginSlice.js';

export default function Login() {
  const dispatch = useDispatch();
  function handleSubmit(e) {
    e.preventDefault();
    const formData = { login: e.target.querySelector("input#jarr-login").value,
                       password: e.target.querySelector("input#jarr-password").value };
    return dispatch(login(formData));
  };
  return (
    <form className={styles.loginForm} noValidate autoComplete="off"
      onSubmit={handleSubmit}>
      <TextField required id="jarr-login" value="prout" label="Login" />
      <TextField required id="jarr-password" value="prout" label="Password" type="password" />
      <Button variant="contained" type="submit">Login</Button>
    </form>
  );
}
