import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
// jarr
import { doSignUp } from "../noAuthSlice";
import useStyles from "./style";

function mapStateToProps(state) {
  return { error: state.noauth.creationError,
  };
}

const mapDispatchToProps = (dispatch) => ({
  signUp(e, formData) {
    e.preventDefault();
    dispatch(doSignUp(formData.login, formData.password, formData.email));
  },
});

function SignUp({ isLoading, error, signUp }) {
  const classes = useStyles();
  const [formData, setFormData] = useState({ login: "", password: "",
                                             passwordConf: "", email: "",
  });
  const passwdNoMatch = formData.password !== formData.passwordConf;
  const [pwdType, setPwdType] = useState("password");
  return (
    <form autoComplete="off" onSubmit={(e) => signUp(e, formData)}>
      <Grid container direction="column">
        <Grid item>
          <TextField required label="Login"
            variant="standard"
            className={classes.loginInput}
            disabled={isLoading}
            error={!!error}
            helperText={error}
            onChange={(e) => setFormData({ ...formData, login: e.target.value })}
          />
        </Grid>
        <Grid item className={classes.passwordGridInput}>
          <TextField required label="Password" type={pwdType}
            variant="standard"
            disabled={isLoading} error={passwdNoMatch}
            helperText={passwdNoMatch ? "Passwords don't match !" : ""}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <IconButton variant="contained"
            onClick={() => setPwdType(pwdType === "text" ? "password": "text")}>
            {pwdType === "text" ? <VisibilityOffIcon /> : <VisibilityIcon />}
          </IconButton>
        </Grid>
        <Grid item>
          <TextField required label="Password confirmation" type={pwdType}
            variant="standard"
            className={classes.loginInput}
            disabled={isLoading} error={passwdNoMatch}
            helperText={passwdNoMatch ? "Should match above !" : ""}
            onChange={(e) => setFormData({ ...formData, passwordConf: e.target.value })}
          />
        </Grid>
        <Grid item>
          <TextField label="Email" type="email"
            variant="standard"
            className={classes.loginInput}
            disabled={isLoading}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            helperText="Not required, but useful for password recovery"
          />
        </Grid>
        <Grid item className={classes.loginButton}>
          <Button variant="contained" type="submit" color="primary">
            Sign Up
          </Button>
        </Grid>
      </Grid>
    </form>
  );
}

SignUp.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  error: PropTypes.string,
};

export default connect(mapStateToProps, mapDispatchToProps)(SignUp);
