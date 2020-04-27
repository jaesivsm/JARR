import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
// jarr
import { doSignUp } from "../noAuthSlice";
import makeStyles from "./style";

function mapStateToProps(state) {
  return { error: state.noauth.creationError,
  };
}

const mapDispatchToProps = (dispatch) => ({
  signUp(e, formData) {
    e.preventDefault();
    return dispatch(doSignUp(formData.login, formData.password, formData.email));
  },
});

function SignUp({ isLoading, error, signUp }) {
  const classes = makeStyles();
  const [formData, setFormData] = useState({
    login: "test", password: "test",
    passwordConf: "test", email: "test@test.com",
  });
  const passwdNoMatch = formData.password !== formData.passwordConf;
  return (
    <form autoComplete="off" onSubmit={(e) => signUp(e, formData)}>
      <Grid item>
        <TextField required label="Login"
          variant="outlined"
          value="test"
          disabled={isLoading}
          error={!!error}
          helperText={error}
          onChange={(e) => setFormData({ ...formData, login: e.target.value })}
        />
      </Grid>
      <Grid item>
        <TextField required label="Password" type="password"
          variant="outlined"
          value="test"
          disabled={isLoading} error={passwdNoMatch}
          helperText={passwdNoMatch ? "Passwords don't match !" : ""}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        />
      </Grid>
      <Grid item>
        <TextField required label="Password confirmation" type="password"
          variant="outlined"
          value="test"
          disabled={isLoading} error={passwdNoMatch}
          helperText={passwdNoMatch ? "Passwords don't match !" : ""}
          onChange={(e) => setFormData({ ...formData, passwordConf: e.target.value })}
        />
      </Grid>
      <Grid item>
        <TextField label="Email" type="email"
          variant="outlined"
          value="test@test.com"
          disabled={isLoading}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
      </Grid>
      <Grid item className={classes.loginButton}>
        <Button variant="contained" type="submit">
          Sign Up
        </Button>
      </Grid>
    </form>
  );
}

SignUp.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  error: PropTypes.string,
};

export default connect(mapStateToProps, mapDispatchToProps)(SignUp);
