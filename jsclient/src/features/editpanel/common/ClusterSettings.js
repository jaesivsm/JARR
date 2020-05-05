import React from "react";
import PropTypes from "prop-types";
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

const clusteringConfOptions = {
    "cluster_enabled": { "label": "Allow article clustering" },
    "cluster_tfidf_enabled": { "label": "Allow article clustering by analysing its content through TFIDF"},
    "cluster_same_category": { "label": "Allow clustering between articles in the same category" },
    "cluster_same_feed": { "label": "Allow clustering between articles inside the same feed" },
    "cluster_wake_up": { "label": "Allow clustering process to unread an article previously marked as read" }
};

export function fillMissingClusterOption(obj, level, def=null) {
  const filledObj = { ...obj };
  Object.keys(clusteringConfOptions)
        .forEach((opt) => {
    if(filledObj[opt] === undefined) {
      filledObj[opt] = def;
    }
  });
  return filledObj;
}

function ClusterSettings({ state, level, setState }) {

  const getHandleChange = (key) => (e, newVal) => {
    setState({ ...state, [key]: e.target.value});
  };

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
        {Object.keys(clusteringConfOptions)
               .map((opt) => (
          <FormControl key={opt} className={classes.editPanelClusterCtrl}>
            <InputLabel id={`${"label-"+opt}`} className={classes.editPanelClusterLabel}>{clusteringConfOptions[opt].label}</InputLabel>
            <Select labelId={`${"label-"+opt}`} id={`${"select-"+opt}`}
              className={classes.editPanelClusterSelect}
              value={`${state[opt] === null && level === "user" ? true : state[opt]}`}
              onChange={getHandleChange(opt)}>
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
    state: PropTypes.object.isRequired,
    level: PropTypes.string.isRequired,
    setState: PropTypes.func.isRequired,
};

export default ClusterSettings;
