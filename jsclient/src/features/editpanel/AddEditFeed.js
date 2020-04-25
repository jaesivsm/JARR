import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Alert from '@material-ui/lab/Alert';
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
// jarr
import { closePanel } from "./editSlice";
import { doCreateObj, doEditObj, doDeleteObj } from "../feedlist/feedSlice";
import { doListClusters } from "../clusterlist/clusterSlice";
import { defaultTo } from "./common";
import StateTextInput from "./common/StateTextInput";
import ClusterSettings, { fillMissingClusterOption } from "./common/ClusterSettings";
import DeleteButton from "./common/DeleteButton";

import editPanelStyle from "./editPanelStyle";

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
    e.preventDefault();
    dispatch(doEditObj(id, feed, "feed"));
    return dispatch(closePanel());
  },
  deleteFeed(e, id) {
    e.preventDefault();
    dispatch(doDeleteObj(id, "feed"));
    dispatch(doListClusters({ categoryId: "all" }));
    return dispatch(closePanel());
  },
});

function ProposedLinks({ link, links, onChange }) {
  return (
      <FormControl>
        <FormHelperText>Other possible feed link have been found :</FormHelperText>
        <Select variant="outlined" value={link}
            onChange={onChange}
        >
            {links.map((proposedLink) => (
              <MenuItem key={"l" + links.indexOf(proposedLink)}
                value={proposedLink}>{proposedLink}</MenuItem>
            ))}
        </Select>
      </FormControl>
  );
}

ProposedLinks.propTypes = {
  link: PropTypes.string.isRequired,
  links: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
};


function AddEditFeed({ job, feed, categories,
                       createFeed, editFeed, deleteFeed }) {
  const currentFeed = fillMissingClusterOption(feed, "feed", null);
  defaultTo(currentFeed, "category_id", null);
  defaultTo(currentFeed, "feed_type", "classic");
  delete currentFeed.links;
  delete currentFeed["same_link_count"];

  const [state, setState] = useState(currentFeed);
  const classes = editPanelStyle();

  let warning;
  if(feed["same_link_count"]) {
    warning = (
      <Alert severity="info">
        You have already {feed["same_link_count"]} feed with that link.
      </Alert>
    );
  } else if (!feed.link) {
    warning = (
      <Alert severity="error">
        Provided URL doesn't look like a feed we support and we couldn't find a correct one.
      </Alert>
    );
  }

  let proposedLinks = null;
  if (feed.links) {
    proposedLinks = <ProposedLinks link={feed.link} links={feed.links}
                        onChange={(e) => setState({ ...state, link: e.target.value})}
                    />;
  }
  return (
    <form onSubmit={(e) => {
      if (!feed.id) { createFeed(e, state); }
      else {editFeed(e, feed.id, state);}
    }}>
    <FormControl component="fieldset">
      {warning}
      <StateTextInput required={true} label="Feed title" name="title"
        state={state} setState={setState} className={classes.editPanelInput}/>
      <StateTextInput label="Feed description" name="description"
        state={state} setState={setState} className={classes.editPanelInput} />
      <StateTextInput required={true} label="Feed link" name="link"
        state={state} setState={setState} className={classes.editPanelInput}/>
      {proposedLinks}
      <StateTextInput label="Website link" name="site_link"
        state={state} setState={setState} className={classes.editPanelInput} />
      <FormControl>
        <FormHelperText>Here you can change the category of the feed :</FormHelperText>
        <Select variant="outlined"
          value={state["category_id"] ? state["category_id"] : 0}
          onChange={(e) => (setState({ ...state, "category_id": e.target.value }))}
          className={classes.editPanelSelect}
        >
          {categories.map((cat) => (
            <MenuItem key={"cat-" + cat.id} value={cat.id ? cat.id: 0}>
              {cat.id ? cat.name : "All"}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl>
        <FormHelperText>A type has been selected for that feed, but you can change it to your liking:</FormHelperText>
        <Select variant="outlined" value={state["feed_type"]}
          onChange={(e) => (setState({ ...state, "feed_type": e.target.value }))}
          className={classes.editPanelSelect}
        >
          {availableFeedTypes.map((type) => (
            <MenuItem key={"item-" + type} value={type}>{type}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <ClusterSettings level="feed" state={state} setState={setState} />
      <Button variant="contained" color="primary" type="submit">
        {job === "add" ? "Create" : "Edit"} Feed
      </Button>
      <DeleteButton id={feed.id} type="feed" deleteFunc={deleteFeed} />
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
