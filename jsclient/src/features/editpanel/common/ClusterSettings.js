import React from "react";
import PropTypes from "prop-types";
// meterial components
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";
import Slider from "@material-ui/core/Slider";
import editPanelStyle from "../editPanelStyle";

const clusteringConfOptions = {
    "cluster_enabled": { "label": "Allow clustering article from this feed" },
    "cluster_tfidf_enabled": { "label": "Allow clustering article by analysing its content through TFIDF"},
    "cluster_same_category": { "label": "Allow cluster article inside the same category" },
    "cluster_same_feed": { "label": "Allow clustering article inside the same feed" },
    "cluster_wake_up": { "label": "Allow clustering to unread an article previously marked as read",
                         "only_for": "feed" }
};

const optionValues = [
    { value: 0, label: 'Off', trueVal: false },
    { value: 1, label: 'Default (from parent)', trueVal: null },
    { value: 2, label: 'On', trueVal: true },
];


const getValLbl = (val) => optionValues.filter((opt) => opt.value === val)[0].label;

const getVal = (val) => {
  const row = optionValues.filter((row) => val === row.value || val === row.trueVal)[0];
  return val === row.trueVal ? row.value : row.trueVal;
}

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
  const getHandleChange = (key) => (e, newVal) => setState({ ...state, [key]: getVal(newVal)});
  const classes = editPanelStyle();
  return (
    <FormControl>
      {Object.keys(clusteringConfOptions)
             .filter(filterOption(level))
             .map((opt) => (
        <>
          <div className={classes.editPanelSlideLabel}>
            {clusteringConfOptions[opt].label}
          </div>
          <FormControlLabel key={"fcl-" + opt} 
            className={classes.editPanelSlide}
            control={<Slider
                      value={getVal(state[opt])}
                      getAriaValueText={getValLbl}
                      marks={level === "user" ? [optionValues[0], optionValues[2]] : optionValues}
                      aria-labelledby="discrete-slider-always"
                      step={null} min={0} max={2}
                      valueLabelDisplay="off"
                      name={opt}
                      onChange={getHandleChange(opt)}
                    />}
          />
        </>
      ))}
    </FormControl>
  );
}

ClusterSettings.propTypes = {
    state: PropTypes.object.isRequired,
    level: PropTypes.string.isRequired,
    setState: PropTypes.func.isRequired,
};

export default ClusterSettings;
