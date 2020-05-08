import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
// jarr
import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj, doDeleteObj } from "../feedlist/feedSlice";
import { doListClusters } from "../clusterlist/clusterSlice";
import ClusterSettings from "./common/ClusterSettings";
import DeleteButton from "./common/DeleteButton";
import StateTextInput from "./common/StateTextInput";

import editPanelStyle from "./editPanelStyle";

const mapDispatchToProps = (dispatch) => ({
  createCategory(e) {
    e.preventDefault();
    dispatch(doCreateObj("category"));
    return dispatch(closePanel());
  },
  editCategory(e, id) {
    e.preventDefault();
    dispatch(doEditObj(id, "category"));
    return dispatch(closePanel());
  },
  deleteCategory(e, id) {
    e.preventDefault();
    dispatch(doDeleteObj(id, "category"));
    dispatch(doListClusters({ categoryId: "all" }));
    return dispatch(closePanel());
  },
});

function mapStateToProps(state) {
  return { catId: state.edit.loadedObj.id };
}

function AddEditCategory({ job, catId,
                           createCategory, editCategory, deleteCategory }) {
  const classes = editPanelStyle();

  return (
    <form onSubmit={(e) => {
      if (job === "add") {
        createCategory(e);
      } else {
        editCategory(e);
      }
    }}>
    <FormControl component="fieldset">
      <StateTextInput label="Category name" name="name"
        className={classes.editPanelInput} />
      />
      <ClusterSettings level="category" />
      <div className={classes.editPanelButtons}>
        <Button className={classes.editPanelBtn} variant="contained" color="primary" type="submit">
          {job === "add" ? "Create" : "Edit"} Category
        </Button>
        <DeleteButton
           type="category" deleteFunc={deleteCategory}
           className={classes.deletePanelBtn} />
      </div>
    </FormControl>
    </form>
  );
}

AddEditCategory.propTypes = {
  job: PropTypes.string.isRequired,
  createCategory: PropTypes.func.isRequired,
  editCategory: PropTypes.func.isRequired,
  deleteCategory: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(AddEditCategory);
