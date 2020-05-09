import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import IconButton from "@material-ui/core/IconButton";
import VisibilityIcon from "@material-ui/icons/Visibility";
import VisibilityOffIcon from "@material-ui/icons/VisibilityOff";
// jarr
import { doRecovery } from "../noAuthSlice";
import makeStyles from "./style";
import { useParams } from "react-router-dom";

function mapStateToProps(state) {
  return { isLoading: state.noauth.loading,
  };
}

const mapDispatchToProps = (dispatch) => ({
  recovery(e, params, password) {
    e.preventDefault();
    dispatch(doRecovery(params.login, params.email, params.token, password));
  },
});

function PasswordRecovery({ isLoading, recovery }) {
  const classes = makeStyles();
  const params = useParams();
  const [pwdType, setPwdType] = useState("password");
  const [password, setPassword] = useState("");
  const [passwordConf, setPasswordConf] = useState("");
  const passwdNoMatch = password !== passwordConf;
  return (
    <form autoComplete="off" onSubmit={(e) => recovery(e, params, password) }>
      <Grid item className={classes.passwordGridInput}>
        <TextField required label="Password" type={pwdType}
          disabled={isLoading} error={passwdNoMatch}
          helperText={passwdNoMatch ? "Passwords don't match !" : ""}
          onChange={(e) => setPassword(e.target.value)}
        />
        <IconButton variant="contained"
          onClick={() => setPwdType(pwdType === "text" ? "password": "text")}>
          {pwdType === "text" ? <VisibilityOffIcon /> : <VisibilityIcon />}
        </IconButton>
      </Grid>
      <Grid item>
        <TextField required label="Password confirmation" type={pwdType}
          className={classes.loginInput}
          disabled={isLoading} error={passwdNoMatch}
          helperText={passwdNoMatch ? "Should match above !" : ""}
          onChange={(e) => setPasswordConf(e.target.value)}
        />
      </Grid>
      <Grid item className={classes.loginButton}>
        <Button variant="contained" type="submit" color="primary">
          Login
        </Button>
      </Grid>
    </form>
  );
}

PasswordRecovery.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  recovery: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(PasswordRecovery);
