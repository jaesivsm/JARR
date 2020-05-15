import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// meterial components
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import Typography from "@material-ui/core/Typography";
import Select from "@material-ui/core/Select";

import editPanelStyle from "../editPanelStyle";
import { editLoadedObj } from "../slice";

const clusteringConfOptions = {
    "cluster_enabled": "Allow article clustering",
    "cluster_tfidf_enabled": "Allow article clustering by analysing its content through TFIDF",
    "cluster_same_category": "Allow clustering between articles in the same category",
    "cluster_same_feed": "Allow clustering between articles inside the same feed",
    "cluster_wake_up": "Allow clustering process to unread an article previously marked as read"
};

function mapStateToProps(state) {
  const clusterOptions = {};
  Object.keys(clusteringConfOptions).forEach((opt) => {
      clusterOptions[opt] = typeof(state.edit.loadedObj[opt]) !== "undefined" ? state.edit.loadedObj[opt] : null;
});
  return { clusterOptions };
}

const mapDispatchToProps = (dispatch) => ({
  edit(e, key) {
    dispatch(editLoadedObj({key, value: e.target.value }));
  },
});

function ClusterSettings({ level, clusterOptions, edit }) {
  const classes = editPanelStyle();

  return (
    <ExpansionPanel className={classes.editPanelCluster} >
      <ExpansionPanelSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls="panel1a-content"
        id="panel1a-header"
      >
        <Typography className={classes.heading}>Cluster Settings</Typography>
      </ExpansionPanelSummary>
      <ExpansionPanelDetails className={classes.editPanelClusterSettings}>
        {Object.entries(clusteringConfOptions)
               .map(([opt, label]) => (
          <FormControl key={opt} className={classes.editPanelClusterCtrl}>
            <InputLabel id={`label-${opt}`} className={classes.editPanelClusterLabel}>{label}</InputLabel>
            <Select labelId={`label-${opt}`} id={`select-${opt}`}
              className={classes.editPanelClusterSelect}
              value={`${clusterOptions[opt] === null && level === "user" ? true : clusterOptions[opt]}`}
              onChange={(e) => edit(e, opt)}>
              {level !== "user" ? <MenuItem value={null}>Default from parent</MenuItem> : null }
              <MenuItem value={true}>Activated</MenuItem>
              <MenuItem value={false}>Deactivated</MenuItem>
            </Select>
          </FormControl>
        ))}
      </ExpansionPanelDetails>
    </ExpansionPanel>
  );
}

ClusterSettings.propTypes = {
  level: PropTypes.string.isRequired,
  clusterOptions: PropTypes.shape({
    "cluster_enabled": PropTypes.bool,
    "cluster_tfidf_enabled": PropTypes.bool,
    "cluster_same_category": PropTypes.bool,
    "cluster_same_feed": PropTypes.bool,
    "cluster_wake_up": PropTypes.bool,
  }),
};

export default connect(mapStateToProps, mapDispatchToProps)(ClusterSettings);
