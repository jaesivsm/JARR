import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
import editPanelStyle from "./editPanelStyle";

import { doBuildFeed } from "./editSlice";

const mapDispatchToProps = (dispatch) => ({
  doBuildFeed(e, feedUrl) {
    e.preventDefault();
    return dispatch(doBuildFeed(feedUrl));
  },
});


function BuildFeed({ isLoading, doBuildFeed }) {
  const [feedUrl, setFeedUrl] = useState(null);
  const classes = editPanelStyle();
  return (
    <form onSubmit={(e) => doBuildFeed(e, feedUrl) }>
    <FormControl component="fieldset">
      <TextField
        required
        id="outlined-required"
        label="Feed Url"
        variant="outlined"
        disabled={isLoading}
        onChange={(e) => (setFeedUrl(e.target.value))}
        className={classes.editPanelInput}
      />
      <FormHelperText>Feed url</FormHelperText>
      <Button disabled={isLoading}
          variant="contained" color="primary" type="submit">
        Build feed from URL
      </Button>
    </FormControl>
    </form>
  );
}

BuildFeed.propTypes = {
  doBuildFeed: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(BuildFeed);
