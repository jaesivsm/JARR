import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
// jarr
import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj, doDeleteObj } from "../feedlist/feedSlice";
import { doListClusters } from "../clusterlist/clusterSlice";
import ClusterSettings, { fillMissingClusterOption } from "./common/ClusterSettings";
import DeleteButton from "./common/DeleteButton";

import editPanelStyle from "./editPanelStyle";

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
  deleteCategory(e, id) {
    e.preventDefault();
    dispatch(doDeleteObj(id, "category"));
    dispatch(doListClusters({ categoryId: "all" }));
    return dispatch(closePanel());
  },
});

function AddEditCategory({ isOpen, job, category,
                           createCategory, editCategory, deleteCategory }) {
  const [state, setState] = useState({
      ...fillMissingClusterOption(category, "category", null),
      "name": category && category.name ? category.name : "",
  });
  const classes = editPanelStyle();

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
        className={classes.editPanelSelect}
      />
      <ClusterSettings level="category" state={state} setState={setState} />
      <Button variant="contained" color="primary" type="submit">
        {job === "add" ? "Create" : "Edit"} Category
      </Button>
      <DeleteButton id={job === "edit" ? category.id : null}
         type="category" deleteFunc={deleteCategory} />
    </FormControl>
    </form>
  );
}

AddEditCategory.propTypes = {
  job: PropTypes.string.isRequired,
  category: PropTypes.object,
  createCategory: PropTypes.func.isRequired,
  editCategory: PropTypes.func.isRequired,
  deleteCategory: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(AddEditCategory);
