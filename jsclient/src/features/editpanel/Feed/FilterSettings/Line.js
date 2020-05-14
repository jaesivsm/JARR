import React from "react";
import PropTypes from "prop-types";
import { createSelector } from "reselect";
import { connect, useDispatch } from "react-redux";
// material ui components
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@material-ui/core/TextField";
import IconButton from "@material-ui/core/IconButton";
import FormControl from "@material-ui/core/FormControl";
// material icons
import MinusIcon from "@material-ui/icons/Remove";
import ArrowUpIcon from "@material-ui/icons/ArrowUpward";
import ArrowDownIcon from "@material-ui/icons/ArrowDownward";
// jarr
import style from "./style";
import { moveUpFilter, moveDownFilter, editFilter, removeFilter
} from "../../slice";
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

const getFilter = (state, props) => state.edit.loadedObj.filters[props.index];
const makeGetFilter = () => createSelector([ getFilter ], (filter) => filter);

const makeMapStateToProps = () => {
  const madeGetFilter = makeGetFilter();
  return (state, props) => ({ filter: madeGetFilter(state, props) });
};

const FilterSettingLine = ({ index, position, filter }) => {
  let moveUpBtn;
  let moveDownBtn;
  const dispatch = useDispatch();
  const classes = style();
  if (position !== "first") {
    moveUpBtn = (
      <IconButton onClick={() => dispatch(moveUpFilter(index))}
          className={classes.editPanelFilterArrow} color="primary">
        <ArrowUpIcon />
      </IconButton>);
  }
  if (position !== "last") {
    moveDownBtn = (
      <IconButton onClick={() => dispatch(moveDownFilter(index))}
          className={classes.editPanelFilterArrow} color="primary">
        <ArrowDownIcon />
      </IconButton>
    );
  }
  const onChange = (key) => (e) => dispatch(editFilter({ index, key, value: e.target.value }));
  return (
    <div className={classes.editPanelFilter}>
      <div className={classes.editPanelFilterArrows}>
        {moveUpBtn}{moveDownBtn}
      </div>
      <FormControl key="trigger" className={classes.editPanelFilterItem}>
        <Select value={filter["action on"]} onChange={onChange("action on")}>
          {Object.entries(FiltersTrigger).map(([trigger, label]) => (
            <MenuItem key={trigger} value={trigger}>{label}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="type" className={classes.editPanelFilterItem}>
        <Select value={filter.type} onChange={onChange("type")}>
          {Object.entries(FiltersType).map(([type, label]) => (
            <MenuItem key={type} value={type}>{label}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl key="pattern" className={classes.editPanelFilterItem}>
        <TextField value={filter.pattern} required onChange={onChange("pattern")} />
      </FormControl>
      <FormControl key="action" className={classes.editPanelFilterItem}>
        <Select value={filter.action} onChange={onChange("action")} >
          {Object.entries(FiltersAction).map(([action, label]) => (
            <MenuItem key={action} value={action}>{label}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <IconButton color="primary" onClick={() => dispatch(removeFilter(index))}
                  className={classes.editPanelFilterDelBtn}>
        <MinusIcon />
      </IconButton>
    </div>
  );
};

FilterSettingLine.propTypes = {
  index: PropTypes.number.isRequired,
  position: PropTypes.string.isRequired,
};

export default connect(makeMapStateToProps)(FilterSettingLine);
