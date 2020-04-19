import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Switch from "@material-ui/core/Switch";
import FormControl from "@material-ui/core/FormControl";
import FormLabel from "@material-ui/core/FormLabel";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormHelperText from "@material-ui/core/FormHelperText";

import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj } from "../feedlist/feedSlice";

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

function defaultTrue(obj, key) {
  return obj && obj[key] !== undefined && obj[key] !== null ? obj[key] : true;
}

function AddEditCategory({ isOpen, job, category, createCategory, editCategory }) {
  const [state, setState] = useState({
      "name": category && category.name ? category.name : "",
      "cluster_enabled": defaultTrue(category, "cluster_enabled"),
      "cluster_tfidf_enabled": defaultTrue(category, "cluster_tfidf_enabled"),
      "cluster_same_category": defaultTrue(category, "cluster_same_category"),
      "cluster_same_feed": defaultTrue(category, "cluster_same_feed"),
  });

  const handleChange = (e) => {
    setState({ ...state, [e.target.name]: e.target.checked });
  };
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
      <FormLabel component="legend">Create a new category</FormLabel>
      <FormGroup>
        <FormControlLabel
          control={<Switch checked={state["cluster_enabled"]} onChange={handleChange} name="cluster_enabled" />}
          label="Enable cluster"
        />
        <FormControlLabel
          control={<Switch checked={state["cluster_tfidf_enabled"]} onChange={handleChange} name="cluster_tfidf_enabled" />}
          label="Enable Clustering through TFIDF"
        />
        <FormControlLabel
          control={<Switch checked={state["cluster_same_category"]} onChange={handleChange} name="cluster_same_category" />}
          label="Enable clustering inside this category"
        />
        <FormControlLabel
          control={<Switch checked={state["cluster_same_feed"]} onChange={handleChange} name="cluster_same_feed" />}
          label="Enable clustering between feeds of this category"
        />
      </FormGroup>
      <FormHelperText>Clustering is one of the defining force of JARR, we encourage you to leave it all to default :)</FormHelperText>
      <Button variant="contained" color="primary" type="submit">
        Create Category
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
