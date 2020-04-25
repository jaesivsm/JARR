import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material component
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Button from "@material-ui/core/Button";
import Switch from "@material-ui/core/Switch";
import FormControl from "@material-ui/core/FormControl";
import TextField from "@material-ui/core/TextField";
// jarr
import StateTextInput from "./common/StateTextInput";
import ClusterSettings, { fillMissingClusterOption } from "./common/ClusterSettings";
import { closePanel } from "./editSlice";
import { doEditObj } from "../feedlist/feedSlice";
import editPanelStyle from "./editPanelStyle";

const mapDispatchToProps = (dispatch) => ({
  editSettings(e, settings, password) {
    if (password) {
      dispatch(doEditObj(null, { ...settings, password }, "user"));
    } else {
      dispatch(doEditObj(null, settings, "user"));
    }
    return dispatch(closePanel());
  },
});

function SettingsPanel({ user, editSettings }) {
  const [state, setState] = useState(fillMissingClusterOption(user, "user", null));
  const [pwdVal, setPwd] = useState("");
  const [pwdConfirm, setPwdConfirm] = useState("");
  const [showPasswd, setShowPasswd] = useState(false);
  const classes = editPanelStyle();
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      if (pwdVal === pwdConfirm) {
        editSettings(e, state, pwdVal);
      }
    }}>
    <FormControl component="fieldset">
      {["login", "email", "timezone"].map((key) => (
          <StateTextInput key={key} label={key} name={key} state={state} setState={setState} disabled={key === "login"}  className={classes.editPanelInput}  />
       ))}
      <ClusterSettings level="user" state={state} setState={setState} />
      <TextField label="Password" variant="outlined"
        className={classes.editPanelInput}
        value={pwdVal}
        error={pwdConfirm !== pwdVal}
        type={showPasswd ? "text" : "password"}
        onChange={(e) => setPwd(e.target.value)} />
      <TextField label="Password confirmation" variant="outlined"
        className={classes.editPanelInput}
        value={pwdConfirm}
        error={pwdConfirm !== pwdVal}
        type={showPasswd ? "text" : "password"}
        onChange={(e) => setPwdConfirm(e.target.value)} />
      <FormControlLabel control={<Switch
        checked={showPasswd}
        onChange={() => setShowPasswd(!showPasswd)}
        color="primary"
        name="checkedB"
        inputProps={{ 'aria-label': 'primary checkbox' }}
      />} label="Show password" />
      <Button variant="contained" color="primary" type="submit" className={classes.editPanelBtn}>
        Edit settings
      </Button>
    </FormControl>
    </form>
  );
}

SettingsPanel.propTypes = {
  user: PropTypes.object.isRequired,
  editSettings: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(SettingsPanel);
