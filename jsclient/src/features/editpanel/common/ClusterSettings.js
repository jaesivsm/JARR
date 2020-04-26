import React from "react";
import PropTypes from "prop-types";
// meterial components
import FormControl from "@material-ui/core/FormControl";
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import InputLabel from '@material-ui/core/InputLabel';
import editPanelStyle from "../editPanelStyle";

const clusteringConfOptions = {
    "cluster_enabled": { "label": "Allow clustering article from this feed" },
    "cluster_tfidf_enabled": { "label": "Allow clustering article by analysing its content through TFIDF"},
    "cluster_same_category": { "label": "Allow cluster article inside the same category" },
    "cluster_same_feed": { "label": "Allow clustering article inside the same feed" },
    "cluster_wake_up": { "label": "Allow clustering to unread an article previously marked as read",
                         "only_for": "feed" }
};

const filterOption = (level) => ((opt) => (
  !clusteringConfOptions[opt].only_for || clusteringConfOptions[opt].only_for === level)
);

export function fillMissingClusterOption(obj, level, def=null) {
  const filledObj = { ...obj };
  Object.keys(clusteringConfOptions)
        .filter(filterOption(level))
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
    console.log(e.target.value);
  }


  return (
    <>
      {Object.keys(clusteringConfOptions)
             .filter(filterOption(level))
             .map((opt) => (
        <FormControl key={opt}> 
          <InputLabel id={`${'label-'+opt}`}>{clusteringConfOptions[opt].label}</InputLabel>
          <Select labelId={`${'label-'+opt}`} id={`${'select-'+opt}`} 
            value={`${state[opt] === null && level === 'user' ? true : state[opt]}`} 
            onChange={getHandleChange(opt)}>
            {level !== 'user' ? <MenuItem value={null}>Default from parent</MenuItem> : null }
            <MenuItem value={true}>Activated</MenuItem>
            <MenuItem value={false}>Deactivated</MenuItem>
          </Select>
        </FormControl>
      ))}
    </>
  );
}

ClusterSettings.propTypes = {
    state: PropTypes.object.isRequired,
    level: PropTypes.string.isRequired,
    setState: PropTypes.func.isRequired,
};

export default ClusterSettings;
