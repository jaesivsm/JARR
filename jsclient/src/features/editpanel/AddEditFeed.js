import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
// jarr
import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj } from "../feedlist/feedSlice";
import { defaultTo } from "./common";
import StateTextInput from "./common/StateTextInput";
import ClusterSettings, { fillMissingClusterOption } from "./common/ClusterSettings";

const availableFeedTypes = ["classic", "json", "tumblr", "instagram",
                            "soundcloud", "reddit", "fetch", "koreus",
                            "twitter"];

const mapDispatchToProps = (dispatch) => ({
  createFeed(e, feed) {
    e.preventDefault();
    if (!feed["category_id"]) {
      delete feed["category_id"];
    }
    dispatch(doCreateObj(feed, "category"));
    return dispatch(closePanel());
  },
  editFeed(e, id, feed) {
      console.log(feed);
    e.preventDefault();
    dispatch(doEditObj(id, feed, "feed"));
    return dispatch(closePanel());
  },
});


function AddEditFeed({ job, feed, categories, createFeed, editFeed }) {
  const currentFeed = fillMissingClusterOption(feed, "feed", null);
  defaultTo(currentFeed, "category_id", null);
  defaultTo(currentFeed, "feed_type", "classic");
  // putting all conf option to default true

  const [state, setState] = useState(currentFeed);
  return (
    <form onSubmit={(e) => {
      if (!feed.id) { createFeed(e, state); }
      else {editFeed(e, feed.id, state);}
    }}>
    <FormControl component="fieldset">
      <StateTextInput required={true} label="Feed title" name="title"
        state={state} setState={setState} />
      <StateTextInput label="Feed description" name="description"
        state={state} setState={setState} />
      <StateTextInput required={true} label="Feed link" name="link"
        state={state} setState={setState} />
      <StateTextInput label="Website link" name="site_link"
        state={state} setState={setState} />
      <Select variant="outlined"
        value={state["category_id"] ? state["category_id"] : 0}
        onChange={(e) => (setState({ ...state, "category_id": e.target.value }))}
      >
        {categories.map((cat) => (
          <MenuItem key={"cat-" + cat.id} value={cat.id ? cat.id: 0}>
            {cat.id ? cat.name : "All"}
          </MenuItem>
        ))}
      </Select>
      <Select variant="outlined" value={state["feed_type"]}
        onChange={(e) => (setState({ ...state, "feed_type": e.target.value }))}
      >
        {availableFeedTypes.map((type) => (
          <MenuItem key={"item-" + type} value={type}>{type}</MenuItem>
        ))}
      </Select>
      <ClusterSettings level="feed" state={state} setState={setState} />
      <Button variant="contained" color="primary" type="submit">
        {job === "add" ? "Create" : "Edit"} Feed
      </Button>
    </FormControl>
    </form>
  );
}

AddEditFeed.propTypes = {
  job: PropTypes.string.isRequired,
  feed: PropTypes.object.isRequired,
  categories: PropTypes.array.isRequired,
  createFeed: PropTypes.func.isRequired,
  editFeed: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(AddEditFeed);
