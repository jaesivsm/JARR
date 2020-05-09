import React from "react";
import { connect } from "react-redux";
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
import { editLoadedObj } from "../editSlice";
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

function mapStateToProps(state) {
  return { filters: state.edit.loadedObj.filters ? state.edit.loadedObj.filters : [],
  };
}
const mapDispatchToProps = (dispatch) => ({
  edit(value) {
    return dispatch(editLoadedObj({ key: "filters", value }));
  },
});

function FilterSettingLineComponent({ index, length, action, trigger, pattern, type, filters, edit }) {
  let moveUp;
  let moveDown;
  const classes = editPanelStyle();
  if (index !== 0) {
    moveUp = (
      <IconButton onClick={() => edit(
          [ ...filters.slice(0, index - 1),
            filters[index],
            filters[index - 1],
            ...filters.slice(index + 1)])}
          className={classes.editPanelFilterArrow} color="primary">
        <ArrowUpIcon />
      </IconButton>);
  }
  if (index !== length - 1 ) {
    moveDown = (
      <IconButton onClick={() => edit(
          [ ...filters.slice(0, index),
            filters[index + 1],
            filters[index],
            ...filters.slice(index + 2)])}
          className={classes.editPanelFilterArrow} color="primary">
        <ArrowDownIcon />
      </IconButton>
    );
  }
  const onChange = (key) => (e) => edit(
    [ ...filters.slice(0, index),
      { ...filters[index], [key]: e.target.value },
      ...filters.slice(index + 1)]);
  return (
    <div className={classes.editPanelFilter}>
      <div className={classes.editPanelFilterArrows}>
        {moveUp}{moveDown}
      </div>
      <FormControl key="trigger" className={classes.editPanelFilterItem}>
        <Select value={trigger} onChange={onChange("action on")}>
          {Object.keys(FiltersTrigger).map((trigger) => (
            <MenuItem key={trigger} value={trigger}>
              {FiltersTrigger[trigger]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="type" className={classes.editPanelFilterItem}>
        <Select value={type} onChange={onChange("type")}>
          {Object.keys(FiltersType).map((type) => (
            <MenuItem key={type} value={type}>{FiltersType[type]}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="pattern" className={classes.editPanelFilterItem}>
        <TextField value={pattern} required onChange={onChange("pattern")} />
      </FormControl>
      <FormControl key="action" className={classes.editPanelFilterItem}>
        <Select value={action} onChange={onChange("action")} >
          {Object.keys(FiltersAction).map((action) => (
            <MenuItem key={action} value={action}>
              {FiltersAction[action]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <IconButton onClick={() => edit(
            [ ...filters.slice(0, index),
              ...filters.slice(index + 1)])}
        className={classes.editPanelFilterDelBtn}
        color="primary"
      >
        <MinusIcon />
      </IconButton>
    </div>
  );
}

FilterSettingLineComponent.propTypes = {
  action: PropTypes.string.isRequired,
  trigger: PropTypes.string.isRequired,
  pattern: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
};

const FilterSettingLine = connect(mapStateToProps, mapDispatchToProps)(FilterSettingLineComponent);

function FilterSettings({ filters, edit }) {
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

        {filters.map((filter, i) =>
          <FilterSettingLine
            key={"filter"+i}
            index={i}
            length={filters.length}
            action={filter.action}
            trigger={filter["action on"]}
            pattern={filter.pattern}
            type={filter.type}
          />
        )}
        <div className={classes.editPanelFilterAddBtn}>
          <Fab onClick={() => edit([ ...filters,
                                    { ...defaultFilter }])}
               color="primary">
            <PlusIcon />
          </Fab>
        </div>
      </ExpansionPanelDetails>
    </ExpansionPanel>
  );
}

FilterSettings.propTypes = {
  filters: PropTypes.array.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(FilterSettings);
