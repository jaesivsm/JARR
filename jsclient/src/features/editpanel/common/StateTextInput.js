import React from "react";
import TextField from "@material-ui/core/TextField";

export default function StateTextInput({ label, name, state, setState, required, disabled, classes }) {
  const onChange = (e) => (setState({ ...state, [e.target.name]: e.target.value }));
  return (
    <TextField required={!!required} disabled={!!disabled} variant="outlined"
               label={label} name={name} value={state[name]}
               onChange={onChange} className={classes} />
  );
}
