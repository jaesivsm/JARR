import React from "react";
import PropTypes from "prop-types";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@material-ui/core/TextField";


const FiltersAction = ['mark as read', 'mark as unread', 'mark as favorite',
                       'mark as unliked', 'skipped', 'unskipped',
                       'allow clustering', 'disallow clustering'];
const FiltersType = ['regex', 'simple match', 'exact match',
                     'tag match', 'tag contains'];
const FiltersTrigger = ['match', 'no match'];


function FilterSettingLine({ action, trigger, pattern, type }) {
  return (
    <div>
      <Select value={action}>
        {FiltersAction.map((action) => (
           <MenuItem key={action} value={action}>{action}</MenuItem>
         ))}
      </Select>
      <Select value={trigger}>
        {FiltersType.map((type) => (
           <MenuItem key={type} value={type}>{type}</MenuItem>
         ))}
      </Select>
      <TextField value={pattern} />
      <Select value={type}>
        {FiltersTrigger.map((trigger) => (
           <MenuItem key={trigger} value={trigger}>{trigger}</MenuItem>
         ))}
      </Select>
    </div>
  );
}

FilterSettingLine.propTypes = {
  action: PropTypes.string.isRequired,
  trigger: PropTypes.string.isRequired,
  pattern: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
};

function FilterSettings({ filters }) {
  return (
    <FormControl>
      {filters.map((filter) =>
          <FilterSettingLine
            action={filter.action}
            trigger={filter["action on"]}
            pattern={filter.pattern}
            type={filter.type}
          />
      )}
    </FormControl>
  );
}

FilterSettings.propTypes = {
  filters: PropTypes.array.isRequired,
};

export default FilterSettings;
