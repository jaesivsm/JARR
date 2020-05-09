import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import Button from "@material-ui/core/Button";
import WarningIcon from "@material-ui/icons/Warning";
import { closePanel } from "../editSlice";
import { doListClusters } from "../../clusterlist/clusterSlice";
import { doDeleteObj } from "../../feedlist/feedSlice";

function mapStateToProps(state) {
  return { id: state.edit.loadedObj.id, };
}

const mapDispatchToProps = (dispatch) => ({
  deleteFunc(e, id, objType) {
    e.preventDefault();
    dispatch(doDeleteObj(objType));
    dispatch(doListClusters({ categoryId: "all" }));
    dispatch(closePanel());
  },
});

function DeleteButton({ id, type, deleteFunc, className }) {
  if (!id) {
    return null;
  }
  return (
    <Button variant="contained" color="default" type="submit"
      onClick={(e) => deleteFunc(e, id)} className={className}>
      <WarningIcon />
      Delete {type}
    </Button>
  );
}

DeleteButton.propTypes = {
  id: PropTypes.number,
  type: PropTypes.string.isRequired,
  deleteFunc: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(DeleteButton);
