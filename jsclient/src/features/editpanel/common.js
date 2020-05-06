import React from "react";
import TextField from "@material-ui/core/TextField";

export function defaultTo(obj, key, defaultValue) {
  if(obj[key] === null || obj[key] === undefined) {
    obj[key] = defaultValue;
  }
}

export function StateTextInput({ label, name, state, setState, required, disabled }) {
  return (
    <TextField required={!!required} disabled={!!disabled} variant="outlined"
      label={label} name={name} value={state[name]}
      onChange={(e) => (setState({ ...state, [e.target.name]: e.target.value }))} />
  );
}
