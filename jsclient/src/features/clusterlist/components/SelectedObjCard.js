import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui  components
import IconButton from "@mui/material/IconButton";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import SettingsIcon from "@mui/icons-material/Build";
import Typography from "@mui/material/Typography";
import DeleteIcon from "@mui/icons-material/Delete";
import Switch from "@mui/material/Switch";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
// jarr
import doFetchObjForEdit from "../../../hooks/doFetchObjForEdit";
import doDeleteObj from "../../../hooks/doDeleteObj";
import doListClusters from "../../../hooks/doListClusters";
import ClusterIcon from "../../../components/ClusterIcon";
import { toggleAutoplayChain } from "../slice";
import useStyles from "./style";

const mapStateToProps = (state) => ({
  autoplayChain: state.clusters.autoplayChain,
});

const mapDispatchToProps = (dispatch) => ({
  openEditPanel(id, objType) {
    dispatch(doFetchObjForEdit(objType, id));
  },
  deleteObj(id, type) {
    dispatch(doDeleteObj(id, type));
    dispatch(doListClusters({ categoryId: "all" }));
  },
  toggleAutoplay() {
    dispatch(toggleAutoplayChain());
  },
});

function SelectedObjCard({ id, str, type, iconUrl, errorCount, lastRetrieved,
                           openEditPanel, deleteObj, autoplayChain, toggleAutoplay }) {
  const objType = type === "feed" ? "feed" : "category";
  const classes = useStyles();

  return (
    <Card variant="outlined" className={classes.clusterListCard}>
      <CardContent className={classes.clusterListCardTitle}>
        {type === "feed" ? <ClusterIcon iconUrl={iconUrl} /> : null}
        <Typography>{str}</Typography>
      </CardContent>
      <CardActions className={classes.clusterListCardActions}>
        <Tooltip title={autoplayChain ? "Disable media autoplay chain" : "Enable media autoplay chain"}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, cursor: "pointer" }} onClick={toggleAutoplay}>
            <PlaylistPlayIcon fontSize="small" color={autoplayChain ? "primary" : "disabled"} />
            <Switch
              checked={autoplayChain}
              onChange={toggleAutoplay}
              size="small"
              color="primary"
            />
          </Box>
        </Tooltip>
        <IconButton size="small"
          onClick={() => openEditPanel(id, objType)}
          className={classes.clusterListCardActionBtn}
      >
         <SettingsIcon size="small" />
        </IconButton>
        <IconButton size="small"
          onClick={() => deleteObj(id, objType)}
          className={classes.clusterListCardActionBtn}
      >
         <DeleteIcon size="small" />
        </IconButton>
      </CardActions>
    </Card>
   );
}

SelectedObjCard.propTypes = {
  id: PropTypes.number.isRequired,
  str: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  iconUrl: PropTypes.string,
  errorCount: PropTypes.number,
  lastRetrieved: PropTypes.string,
  openEditPanel: PropTypes.func.isRequired,
  deleteObj: PropTypes.func.isRequired,
  autoplayChain: PropTypes.bool.isRequired,
  toggleAutoplay: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(SelectedObjCard);
