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

import { doCreateCategory } from "../feedlist/feedSlice";

const mapDispatchToProps = (dispatch) => ({
  createCategory(e, category) {
    e.preventDefault();
    console.log(category);
    return dispatch(doCreateCategory(category));
  },
});

function AddCategory({ isOpen, createCategory }) {
  const [state, setState] = useState({ "name": "",
                                       "cluster_enabled": true,
                                       "cluster_tfidf_enabled": true,
                                       "cluster_same_category": true,
                                       "cluster_same_feed": true })

  const handleChange = (e) => {
    setState({ ...state, [e.target.name]: e.target.checked });
  };

  return (
    <form onSubmit={(e) => createCategory(e, state) }>
    <FormControl component="fieldset">
      <TextField
        required
        id="outlined-required"
        label="Category Name"
        variant="outlined"
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

AddCategory.propTypes = {
  createCategory: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(AddCategory);
