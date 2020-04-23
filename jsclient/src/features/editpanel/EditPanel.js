import React from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Drawer from "@material-ui/core/Drawer";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import Close from "@material-ui/icons/Close";
import CircularProgress from "@material-ui/core/CircularProgress";
// jarr
import BuildFeed from "./BuildFeed";
import AddEditFeed from "./AddEditFeed";
import AddEditCategory from "./AddEditCategory";
import SettingsPanel from "./SettingsPanel";
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
           categories: state.feeds.feedListRows.filter((row) => (
               row.type === "categ" || row.type === "all-categ")
           ).map((cat) => ({ id: cat.id, name: cat.str })),
           loadedObj: state.edit.loadedObj,
  };
}

function EditPanel({ isOpen, isLoading, job, objType,
                     buildedFeed, loadedObj, categories,
                     close }) {
  const classes = editPanelStyle();
  let form = <CircularProgress />;
  if(job === "add" && objType === "feed") {
    if(buildedFeed) {
      form = <AddEditFeed job={job} feed={buildedFeed} categories={categories} />;
    } else {
      form = <BuildFeed isLoading={isLoading} />;
    }
  } else if (job === "edit" && objType === "feed") {
    form = <AddEditFeed job={job} feed={loadedObj} categories={categories} />;
  } else if ((job === "add" || job === "edit") && objType === "category") {
    form = <AddEditCategory job={job} category={loadedObj} />;
  } else if (job === "edit" && objType === "user") {
    form = <SettingsPanel user={loadedObj} />
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
      <div className={classes.editPanelForm}>
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
  loadedObj: PropTypes.object,
  close: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(EditPanel);
