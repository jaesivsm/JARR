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
import ClusterSettings from "./common/ClusterSettings";
import { closePanel, editLoadedObj } from "./editSlice";
import { doEditObj } from "../feedlist/feedSlice";
import editPanelStyle from "./editPanelStyle";

const mapDispatchToProps = (dispatch) => ({
  editSettings(settings) {
    dispatch(doEditObj(null, "user"));
    return dispatch(closePanel());
  },
  edit(key, value) {
    return dispatch(editLoadedObj({ key, value }));
  },
});

function SettingsPanel({ editSettings }) {
  const [pwdVal, setPwd] = useState("");
  const [pwdConfirm, setPwdConfirm] = useState("");
  const [showPasswd, setShowPasswd] = useState(false);
  const classes = editPanelStyle();
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      if (pwdVal === pwdConfirm) {
        editSettings(pwdVal);
      }
    }}>
    <FormControl component="fieldset">
      {["login", "email", "timezone"].map((key) => (
          <StateTextInput key={key} label={key} name={key}
            disabled={key === "login"}
            className={classes.editPanelInput}  />
       ))}
      <ClusterSettings level="user" />
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
      />} label="Show password" />
      <Button variant="contained" color="primary" type="submit"
         className={classes.editPanelBtn}>
        Edit settings
      </Button>
    </FormControl>
    </form>
  );
}

SettingsPanel.propTypes = {
  editSettings: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(SettingsPanel);
