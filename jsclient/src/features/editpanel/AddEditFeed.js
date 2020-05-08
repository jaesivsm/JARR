import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Alert from "@material-ui/lab/Alert";
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
// jarr
import { closePanel, editLoadedObj } from "./editSlice";
import { doCreateObj, doEditObj, doDeleteObj } from "../feedlist/feedSlice";
import { doListClusters } from "../clusterlist/clusterSlice";
import StateTextInput from "./common/StateTextInput";
import ClusterSettings from "./common/ClusterSettings";
import FilterSettings from "./common/FilterSettings";
import DeleteButton from "./common/DeleteButton";

import editPanelStyle from "./editPanelStyle";

const availableFeedTypes = ["classic", "json", "tumblr", "instagram",
                            "soundcloud", "reddit", "fetch", "koreus",
                            "twitter"];
const noUrlTypes = ["instagram", "soundcloud", "twitter"];

function mapPropposedLinkStateToProps(state) {
  return { link: state.edit.loadedObj.link,
           links: state.edit.loadedObj.links,
  };
}

const mapPropposedLinkDispatchToProps = (dispatch) => ({
  edit(key, value) {
    return dispatch(editLoadedObj({ key, value }));
  }
});

const mapDispatchToProps = (dispatch) => ({
  createFeed(e, feed) {
    e.preventDefault();
    if (!feed["category_id"]) {
      delete feed["category_id"];
    }
    dispatch(doCreateObj(feed, "feed"));
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
  edit(key, value) {
    return dispatch(editLoadedObj({ key, value }));
  },
});

function ProposedLinksComponent({ link, links, onChange }) {
  const classes = editPanelStyle();
  if (!links) {
    return null;
  }
  return (
      <FormControl>
        <FormHelperText>Other possible feed link have been found :</FormHelperText>
        <Select variant="outlined" value={link}
            onChange={onChange}
            className={classes.editPanelInput}
        >
            {links.map((proposedLink) => (
              <MenuItem key={"l" + links.indexOf(proposedLink)}
                value={proposedLink}>{proposedLink}</MenuItem>
            ))}
        </Select>
      </FormControl>
  );
}

ProposedLinksComponent.propTypes = {
  link: PropTypes.string.isRequired,
  links: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
};

const ProposedLinks = connect(mapPropposedLinkStateToProps,
                              mapPropposedLinkDispatchToProps
)(ProposedLinksComponent);

function mapStateToProps(state) {
  return { catId: state.edit.loadedObj["category_id"] ? state.edit.loadedObj["category_id"] : null,
           feedType: state.edit.loadedObj["feed_type"] ? state.edit.loadedObj["feed_type"] : "classic",
           sameLinkCount: state.edit.loadedObj["same_link_count"],
           link: state.edit.loadedObj.link,
           feedId: state.edit.loadedObj.id,

           };
}

function AddEditFeed({ job, categories, link, sameLinkCount,
                       feedId, catId, feedType,
                       createFeed, editFeed, deleteFeed, edit }) {
  const classes = editPanelStyle();

  let warning;
  if(sameLinkCount) {
    warning = (
      <Alert severity="info">
        You have already {sameLinkCount} feed with that link.
      </Alert>
    );
  } else if (!link) {
    warning = (
      <Alert severity="error">
        Provided URL doesn"t look like a feed we support and we couldn"t find a correct one.
      </Alert>
    );
  }

  const feedTypeHelper = (noUrlTypes.indexOf(feedType) === -1 ? null :
    <Alert severity="info">"{feedType}" type doesn't need a full url for link. Just the username will suffice.</Alert>
  );
  return (
    <form onSubmit={(e) => {
      if (!feedId) { createFeed(e); }
      else {editFeed(e);}
    }}>
    <FormControl component="fieldset">
      {warning}
      <StateTextInput required={true} label="Feed title" name="title"
        className={classes.editPanelInput}/>
      <StateTextInput label="Feed description" name="description"
        className={classes.editPanelInput} />
      <StateTextInput required={true} label="Feed link" name="link"
        className={classes.editPanelInput}/>
      <ProposedLinks />
      <StateTextInput label="Website link" name="site_link"
        className={classes.editPanelInput} />
      <FormControl>
        <FormHelperText>Here you can change the category of the feed :</FormHelperText>
        <Select variant="outlined"
          value={catId ? catId : 0}
          onChange={(e) => edit("category_id", e.target.value)}
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
        <Select variant="outlined" value={feedType}
          onChange={(e) => edit("feed_type", e.target.value)}
          className={classes.editPanelSelect}
        >
          {availableFeedTypes.map((type) => (
            <MenuItem key={"item-" + type} value={type}>{type}</MenuItem>
          ))}
        </Select>
        {feedTypeHelper}
      </FormControl>
      <FilterSettings />
      <ClusterSettings level="feed" />
      <div className={classes.editPanelButtons}>
        <Button className={classes.editPanelBtn} variant="contained" color="primary" type="submit">
          {job === "add" ? "Create" : "Edit"} Feed
        </Button>
        <DeleteButton id={feedId} type="feed" deleteFunc={deleteFeed}
          className={classes.deletePanelBtn}/>
      </div>
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

export default connect(mapStateToProps, mapDispatchToProps)(AddEditFeed);
