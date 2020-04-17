import React from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Drawer from "@material-ui/core/Drawer";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import Close from "@material-ui/icons/Close";

// jarr
import BuildFeed from "./BuildFeed";
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
           isLoading: state.edit.isLoading,
           job: state.edit.job,
           objType: state.edit.objType,
           buildedFeed: state.edit.buildedFeed,
           categories: state.feeds.categories.map((cat) => (
               { id: cat.id, name: cat.name }
           )),
  };
}

function EditPanel({ isOpen, isLoading, job, objType, buildedFeed, categories, close }) {
  const classes = editPanelStyle();
  let form = null;
  if(job === "add" && objType === "feed") {
    if(buildedFeed) {
      form = <AddFeed buildedFeed={buildedFeed} categories={categories} />;
    } else {
      form = <BuildFeed isLoading={isLoading} />;
    }
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
        <Typography className={classes.editPanelTitle}>
          {job.charAt(0).toUpperCase()}{job.slice(1)}ing {objType.charAt(0).toUpperCase()}{objType.slice(1)}
        </Typography>
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
  isLoading: PropTypes.bool.isRequired,
  categories: PropTypes.array,
  job: PropTypes.string,
  objType: PropTypes.string,
  buildedFeed: PropTypes.object,
  close: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(EditPanel);
