import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Alert from "@material-ui/lab/Alert";
import Switch from "@material-ui/core/Switch";
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormHelperText from "@material-ui/core/FormHelperText";
// jarr
import { closePanel, editLoadedObj } from "./editSlice";
import { doCreateObj, doEditObj } from "../feedlist/feedSlice";
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
  edit(value) {
    dispatch(editLoadedObj({ key: "link", value }));
  }
});


function ProposedLinksComponent({ link, links, edit }) {
  const classes = editPanelStyle();
  if (!links) {
    return null;
  }
  return (
      <FormControl>
        <FormHelperText>Other possible feed link have been found :</FormHelperText>
        <Select variant="outlined" value={link}
            onChange={(e) => edit(e.target.value)}
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
  link: PropTypes.string,
  links: PropTypes.array,
  edit: PropTypes.func.isRequired,
};

const ProposedLinks = connect(mapPropposedLinkStateToProps,
                              mapPropposedLinkDispatchToProps
)(ProposedLinksComponent);

function extractFromLoadedObj(state, key, def) {
  if (state.edit.loadedObj && state.edit.loadedObj[key] !== undefined) {
      return state.edit.loadedObj[key];
  }
  return def;
}

const mapDispatchToProps = (dispatch) => ({
  commit(e, job) {
    e.preventDefault();
    if (job === "edit") {
      dispatch(doEditObj("feed"));
    } else {
      dispatch(doCreateObj("feed"));
    }
    dispatch(closePanel());
  },
  edit(key, value) {
    dispatch(editLoadedObj({ key, value }));
  },
});

function mapStateToProps(state) {
  return { catId: extractFromLoadedObj(state, "category_id", null),
           feedType: extractFromLoadedObj(state, "feed_type", "classic"),
           sameLinkCount: extractFromLoadedObj(state, "same_link_count", 0),
           link: extractFromLoadedObj(state, "link", ""),
           feedId: extractFromLoadedObj(state, "id", null),
           active: extractFromLoadedObj(state, "status", "active") === "active",
           categories: state.feeds.feedListRows.filter((row) => (
               row.type === "categ" || row.type === "all-categ")
           ).map((cat) => ({ id: cat.id, name: cat.str })),
           };
}

function AddEditFeed({ job, categories, link, sameLinkCount,
                       feedId, catId, feedType, active,
                       edit, commit }) {
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
    <form onSubmit={(e) => commit(e, job)}>
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
      <FormControlLabel
        control={<Switch color="primary" checked={active}
                    onChange={() => edit("status", active ? "paused" : "active")} />}
        label="Active feed" />
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
      {!feedId ? <Alert>
        Your feed will be created but articles won't appear right away. It might take a little while before you see content appear. Be patient :)
      </Alert>: null}
      <div className={classes.editPanelButtons}>
        <Button className={classes.editPanelBtn}
          variant="contained" color="primary" type="submit">
          {!feedId ? "Create" : "Edit"} Feed
        </Button>
        <DeleteButton type="feed" className={classes.deletePanelBtn}/>
      </div>
    </FormControl>
    </form>
  );
}

AddEditFeed.propTypes = {
  link: PropTypes.string,
  sameLinkCount: PropTypes.number.isRequired,
  feedId: PropTypes.number,
  catId: PropTypes.number,
  feedType: PropTypes.string.isRequired,
  active: PropTypes.bool.isRequired,
  job: PropTypes.string.isRequired,
  categories: PropTypes.array.isRequired,
  edit: PropTypes.func.isRequired,
  commit: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(AddEditFeed);
