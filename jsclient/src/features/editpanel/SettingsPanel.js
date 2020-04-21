import React, { useState } from "react";
import { openPanel } from "../editpanel/editSlice";
import { connect } from "react-redux";
// material component
import FormControl from "@material-ui/core/FormControl";
// jarr
import StateTextInput from "./common/StateTextInput";
import ClusterSettings from "./common/ClusterSettings";

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
      <ClusterSettings level="user" state={state} setState={setState} />
    </FormControl>
    </form>
  );
}

export default connect(null, mapDispatchToProps)(SettingsPanel);
