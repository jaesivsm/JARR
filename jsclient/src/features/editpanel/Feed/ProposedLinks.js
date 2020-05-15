import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material components
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormHelperText from "@material-ui/core/FormHelperText";
// jarr
import editPanelStyle from "../editPanelStyle";
import { editLoadedObj } from "../slice";

const mapStateToProps = (state) => ({
  link: state.edit.loadedObj.link,
  links: state.edit.loadedObj.links,
});

const mapDispatchToProp = (dispatch) => ({
  edit(value) {
    dispatch(editLoadedObj({ key: "link", value }));
  }
});

const ProposedLinks = ({ link, links, edit }) => {
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
          <MenuItem key={`l${links.indexOf(proposedLink)}`}
          value={proposedLink}>{proposedLink}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

ProposedLinks.propTypes = {
  link: PropTypes.string,
  links: PropTypes.array,
  edit: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProp)(ProposedLinks);
