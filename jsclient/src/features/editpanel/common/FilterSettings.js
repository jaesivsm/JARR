import React from "react";
import PropTypes from "prop-types";
// material ui components
import Fab from "@material-ui/core/Fab";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import IconButton from "@material-ui/core/IconButton";
// material icons
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import ArrowUpIcon from "@material-ui/icons/ArrowUpward";
import ArrowDownIcon from "@material-ui/icons/ArrowDownward";
import PlusIcon from "@material-ui/icons/Add";
import MinusIcon from "@material-ui/icons/Remove";
// jarr
import editPanelStyle from "../editPanelStyle";
// constants
const FiltersAction = { "mark as read": "mark as read",
                        "mark as unread": "mark as unread (default)",
                        "mark as favorite": "mark as liked",
                        "mark as unliked": "mark as unliked (default)",
                        "skipped": "skip",
                        "unskipped": "unskip (default)",
                        "allow clustering": "allow clustering (default)",
                        "disallow clustering": "forbid clustering"};
const FiltersType = { "regex": "title match (regex)",
                      "simple match": "title contains",
                      "exact match": "title is",
                      "tag match": "one of the tag is",
                      "tag contains": "one of the tags contains" };
const FiltersTrigger = {"match": "If", "no match": "If not", };
const defaultFilter = { action: "mark as read", "action on": "match",
                        type: "simple match", pattern: "" };


function FilterSettingLine({ index, length, action, trigger, pattern, type, state, setState }) {
  let moveUp;
  let moveDown;
  const classes = editPanelStyle();
  if (index !== 0) {
    moveUp = (
      <IconButton onClick={() =>
        setState({ ...state,
                   filters: [ ...state.filters.slice(0, index - 1),
                              state.filters[index],
                              state.filters[index - 1],
                              ...state.filters.slice(index + 1)],
        })
      } className={classes.editPanelFilterArrow} color="primary">
        <ArrowUpIcon />
      </IconButton>);
  }
  if (index !== length - 1 ) {
    moveDown = (
      <IconButton onClick={() =>
        setState({ ...state,
                   filters: [ ...state.filters.slice(0, index),
                              state.filters[index + 1],
                              state.filters[index],
                              ...state.filters.slice(index + 2)],
        })
      } className={classes.editPanelFilterArrow} color="primary">
        <ArrowDownIcon />
      </IconButton>
    );
  }
  const onChange = (key) => (e) => setState({ ...state,
    filters: [ ...state.filters.slice(0, index),
               { ...state.filters[index], [key]: e.target.value },
               ...state.filters.slice(index + 1), ]});
  return (
    <div className={classes.editPanelFilter}>
      <div className={classes.editPanelFilterArrows}>
        {moveUp}{moveDown}
      </div>
      <FormControl key="trigger" className={classes.editPanelFilterTrigger}>
        <Select value={trigger} onChange={onChange("action on")}>
          {Object.keys(FiltersTrigger).map((trigger) => (
            <MenuItem key={trigger} value={trigger}>
              {FiltersTrigger[trigger]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="type" className={classes.editPanelFilterType}>
        <Select value={type} onChange={onChange("type")}>
          {Object.keys(FiltersType).map((type) => (
            <MenuItem key={type} value={type}>{FiltersType[type]}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="pattern" className={classes.editPanelFilterPattern}>
        <TextField value={pattern} required onChange={onChange("pattern")} />
      </FormControl>
      <FormControl key="action" className={classes.editPanelFilterAction}>
        <Select value={action} onChange={onChange("action")} >
          {Object.keys(FiltersAction).map((action) => (
            <MenuItem key={action} value={action}>
              {FiltersAction[action]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <IconButton onClick={() => setState(
          { ...state,
            filters: [ ...state.filters.slice(0, index),
                       ...state.filters.slice(index + 1)]})}
        className={classes.editPanelFilterDelBtn}
        color="primary"
      >
        <MinusIcon />
      </IconButton>
    </div>
  );
}

FilterSettingLine.propTypes = {
  action: PropTypes.string.isRequired,
  trigger: PropTypes.string.isRequired,
  pattern: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
};

function FilterSettings({ state, setState }) {
  const classes = editPanelStyle();
  return (
    <ExpansionPanel className={classes.editPanelCluster} >
      <ExpansionPanelSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls="panel1a-content"
        id="panel1a-header"
      >
        <Typography className={classes.heading}>Filters Settings</Typography>
      </ExpansionPanelSummary>
      <ExpansionPanelDetails className={classes.editPanelClusterSettings}>

        {state.filters.map((filter, i) =>
          <FilterSettingLine
            key={"filter"+i}
            index={i}
            length={state.filters.length}
            action={filter.action}
            trigger={filter["action on"]}
            pattern={filter.pattern}
            type={filter.type}
            state={state}
            setState={setState}
          />
        )}
        <div className={classes.editPanelFilterAddBtn}>
          <Fab onClick={() => setState({ ...state,
                                                filters: [ ...state.filters,
                                                           { ...defaultFilter }]}
          )} color="primary">
            <PlusIcon />
          </Fab>
        </div>
      </ExpansionPanelDetails>
    </ExpansionPanel>
  );
}

FilterSettings.propTypes = {
  state: PropTypes.object.isRequired,
};

export default FilterSettings;
