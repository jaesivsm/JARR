import React from "react";
import PropTypes from "prop-types";
import Button from "@material-ui/core/Button";
import WarningIcon from "@material-ui/icons/Warning";

function DeleteButton({ id, type, deleteFunc }) {
  if (!id) {
    return null;
  }
  return (
    <Button variant="contained" color="secondary" type="submit"
      onClick={(e) => deleteFunc(e, id)}>
      <WarningIcon />
      Delete this feed
    </Button>
  );
}

DeleteButton.propTypes = {
  id: PropTypes.number,
  type: PropTypes.string.isRequired,
  deleteFunc: PropTypes.func.isRequired,
}

export default DeleteButton;
