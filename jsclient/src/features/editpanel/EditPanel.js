import React from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import Drawer from "@material-ui/core/Drawer";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import Close from "@material-ui/icons/Close";
// jarr
import AddFeed from "./AddFeed";
import AddCategory from "./AddCategory";
import { closePanel } from "./editSlice";
import editPanelStyle from "./editPanelStyle";

const mapDispatchToProps = (dispatch) => ({
  close() {
    return dispatch(closePanel());
  },
});

function mapStateToProps(state) {
  return { isOpen: state.edit.isOpen,
           job: state.edit.job,
           objType: state.edit.objType,
  };
}

function EditPanel({ isOpen, job, objType, close }) {
  const classes = editPanelStyle();
  let form = null;
  if(job === "add" && objType === "feed") {
    form = <AddFeed />;
  } else if (job === "add" && objType === "category") {
    form = <AddCategory />
  }
  return (
    <Drawer
      variant="persistent"
      anchor="right"
      open={isOpen}
      className={classes.editPanel}
      classes={{
        paper: classes.editPanelPaper,
      }}
    >
      <div className={classes.editPanelHeader}>
        <IconButton onClick={close}>
          <Close />
        </IconButton>
      </div>
      <Divider />
      <div>
        {form}
      </div>
    </Drawer>
  );
}

EditPanel.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  job: PropTypes.string,
  objType: PropTypes.string,
  close: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(EditPanel);
