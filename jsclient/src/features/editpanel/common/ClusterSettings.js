import React from "react";
import PropTypes from "prop-types";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Slider from "@material-ui/core/Slider";

const clusteringConfOptions = {
    "cluster_enabled": { "label": "Allow clustering article from this feed" },
    "cluster_tfidf_enabled": { "label": "Allow clustering article by analysing its content through TFIDF"},
    "cluster_same_category": { "label": "Allow cluster article inside the same category" },
    "cluster_same_feed": { "label": "Allow clustering article inside the same feed" },
    "cluster_wake_up": { "label": "Allow clustering to unread an article previously marked as read",
                         "only_for": "feed" }
};

const optionValues = [
    { value: 0, label: 'Desactived', trueVal: false },
    { value: 1, label: 'From Parent', trueVal: null },
    { value: 2, label: 'Activated', trueVal: true },
];


const getValLbl = (val) => optionValues.filter((opt) => opt.value === val)[0].label;

const getVal = (val) => {
  const row = optionValues.filter((row) => val === row.value || val === row.trueVal)[0];
  return val === row.trueVal ? row.value : row.trueVal;
}

function ClusterSettings({ state, level, setState }) {
  function getHandleChange(key) {
    return (e, newVal) => {
        console.log({ ...state });
        console.log(key, newVal, getVal(newVal));
        setState({ ...state, [key]: getVal(newVal)})
        console.log({ ...state });
    };
  }
  return (
    <>
      {Object.keys(clusteringConfOptions)
             .filter((swtch) => (
               !clusteringConfOptions[swtch].only_for || clusteringConfOptions[swtch].only_for === level))
             .map((swtch) => (
        <FormControlLabel key={"fcl-" + swtch}
          control={<Slider
                     value={getVal(state[swtch])}
                     getAriaValueText={getValLbl}
                     marks={optionValues}
                     aria-labelledby="discrete-slider-always"
                     step={null} min={0} max={2}
                     valueLabelDisplay="off"
                     name={swtch}
                     onChange={getHandleChange(swtch)}
                   />}
          label={clusteringConfOptions[swtch].label}
        />
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
