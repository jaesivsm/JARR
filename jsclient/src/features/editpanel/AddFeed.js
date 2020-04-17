import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import Switch from "@material-ui/core/Switch";
import FormControlLabel from "@material-ui/core/FormControlLabel";

import { closePanel } from "./editSlice";
import { doCreateFeed } from "../feedlist/feedSlice";

const availableFeedTypes = ["classic", "json", "tumblr", "instagram",
                            "soundcloud", "reddit", "fetch", "koreus",
                            "twitter"];

const feedConfs = {"cluster_enabled": "Allow clustering article from this feed",
                   "cluster_tfidf_enabled": "Allow clustering article by analysing its content through TFIDF",
                   "cluster_same_category": "Allow cluster article inside the same category",
                   "cluster_same_feed": "Allow clustering article inside the same feed",
                   "cluster_wake_up": "Allow clustering to unread an article previously marked as read"};

const mapDispatchToProps = (dispatch) => ({
  createFeed(e, feed) {
    e.preventDefault();
    if (!feed["category_id"]) {
      delete feed["category_id"];
    }
    dispatch(doCreateFeed(feed));
    return dispatch(closePanel());
  },
});

function FeedTextAttr({ required, label, name, state, setState}) {
  return (
    <TextField required={!!required} variant="outlined"
      label={label} name={name} value={state[name]}
      onChange={(e) => (setState({ ...state, [e.target.name]: e.target.value }))} />
  );
}

function AddFeed({ buildedFeed, categories, createFeed }) {
  const feedToCreate = { ...buildedFeed, "category_id": null };
  // putting all conf option to default true
  Object.keys(feedConfs).forEach((option) => {
    if (feedToCreate[option] === undefined) {
      feedToCreate[option] = true;
    }
  })

  const [state, setState] = useState(feedToCreate);
  const handleSwitchChange = (e) => {
    setState({ ...state, [e.target.name]: e.target.checked});
  };
  return (
    <form onSubmit={(e) => createFeed(e, state) }>
    <FormControl component="fieldset">
      <FeedTextAttr required={true} label="Feed title" name="title"
        state={state} setState={setState} />
      <FeedTextAttr label="Feed description" name="description"
        state={state} setState={setState} />
      <FeedTextAttr required={true} label="Feed link" name="link"
        state={state} setState={setState} />
      <FeedTextAttr label="Website link" name="site_link"
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
      {Object.keys(feedConfs).map((option) => (
        <FormControlLabel key={"fcl-" + option}
          control={<Switch checked={state[option]} color="primary"
                           onChange={(e) => (handleSwitchChange(e))}
                           name={option} />}
          label={feedConfs[option]}
        />
      ))}
      <Button variant="contained" color="primary" type="submit">
        Create Feed
      </Button>
    </FormControl>
    </form>
  );
}

AddFeed.propTypes = {
  buildedFeed: PropTypes.object.isRequired,
  categories: PropTypes.array.isRequired,
  createFeed: PropTypes.func.isRequired,
};

export default connect(null, mapDispatchToProps)(AddFeed);
