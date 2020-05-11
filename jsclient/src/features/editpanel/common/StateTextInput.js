import React from "react";
import { connect } from "react-redux";
import TextField from "@material-ui/core/TextField";

import { editLoadedObj } from "../editSlice";

function mapStateToProps(state) {
  return { loadedObj: state.edit.loadedObj };
}
const mapDispatchToProps = (dispatch) => ({
  edit(e, key) {
    dispatch(editLoadedObj({ key, value: e.target.value }));
  },
});

function StateTextInput({ label, name, loadedObj, edit, required, disabled, className }) {
  return (
    <TextField required={required} disabled={!!disabled} variant="outlined"
               label={label} name={name}
               value={loadedObj[name] ? loadedObj[name] : ""}
               className={className}
               onChange={(e) => edit(e, name)}
    />
  );
}
export default connect(mapStateToProps, mapDispatchToProps)(StateTextInput);
