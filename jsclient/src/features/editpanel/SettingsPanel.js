import React, { useState } from "react";
import { openPanel } from "../editpanel/editSlice";
import { connect } from "react-redux";
// react component
import FormControl from "@material-ui/core/FormControl";
import { StateTextInput } from "./common";

const mapDispatchToProps = (dispatch) => ({
  toggleSettingsPanel(objType) {
    return dispatch(openPanel({ objType }));
  },
});

function SettingsPanel({ user }) {
  const [state, setState] = useState(user);
  return (
    <form>
    <FormControl component="fieldset">
      {["login", "email", "timezone"].map((key) => (
          <StateTextInput label={key} name={key} state={state} setState={setState} disabled={key === "login"} />
       ))}
    </FormControl>
    </form>
  );
}

export default connect(null, mapDispatchToProps)(SettingsPanel);
