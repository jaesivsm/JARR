import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
// jarr
import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj } from "../feedlist/feedSlice";
import ClusterSettings, { fillMissingClusterOption } from "./common/ClusterSettings";

const mapDispatchToProps = (dispatch) => ({
  createCategory(e, category) {
    e.preventDefault();
    dispatch(doCreateObj(category, "category"));
    return dispatch(closePanel());
  },
  editCategory(e, id, category) {
    e.preventDefault();
    dispatch(doEditObj(id, category, "category"));
    return dispatch(closePanel());
  },
});

function AddEditCategory({ isOpen, job, category, createCategory, editCategory }) {
  const [state, setState] = useState({
      ...fillMissingClusterOption(category, "category", null),
      "name": category && category.name ? category.name : "",
  });

  return (
    <form onSubmit={(e) => {
      if (job === "add") {
        createCategory(e, state);
      } else {
        editCategory(e, category.id, state);
      }
    }}>
    <FormControl component="fieldset">
      <TextField
        required
        id="outlined-required"
        label="Category Name"
        variant="outlined"
        value={state.name}
        onChange={(e) => (setState({ ...state, name: e.target.value }))}
      />
      <ClusterSettings level="category" state={state} setState={setState} />
      <Button variant="contained" color="primary" type="submit">
        {job === "add" ? "Create" : "Edit"} Category
      </Button>
    </FormControl>
    </form>
  );
}

AddEditCategory.propTypes = {
  job: PropTypes.string.isRequired,
  category: PropTypes.object,
  createCategory: PropTypes.func.isRequired,
  editCategory: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(AddEditCategory);
