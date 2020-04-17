import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormLabel from "@material-ui/core/FormLabel";
import FormHelperText from "@material-ui/core/FormHelperText";
import CircularProgress from "@material-ui/core/CircularProgress";

import { doBuildFeed } from "./editSlice";

const mapDispatchToProps = (dispatch) => ({
  doBuildFeed(e, feedUrl) {
    e.preventDefault();
    return dispatch(doBuildFeed(feedUrl));
  },
});


function BuildFeed({ isLoading, doBuildFeed }) {
  const [feedUrl, setFeedUrl] = useState(null);
  return (
    <form onSubmit={(e) => doBuildFeed(e, feedUrl) }>
    <FormControl component="fieldset">
      <FormLabel component="legend">Create a new category</FormLabel>
      <TextField
        required
        id="outlined-required"
        label="Feed Url"
        variant="outlined"
        disabled={isLoading}
        onChange={(e) => (setFeedUrl(e.target.value))}
      />
      <FormHelperText>Feed url</FormHelperText>
      <Button disabled={isLoading}
          variant="contained" color="primary" type="submit">
        Build feed from URL
      </Button>
      {isLoading ? <CircularProgress /> : null}
    </FormControl>
    </form>
  );
}

BuildFeed.propTypes = {
  doBuildFeed: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(BuildFeed);
