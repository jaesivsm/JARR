import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui  components
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
// jarr
import { doFetchObjForEdit } from "../../editpanel/editSlice";
import { doDeleteObj } from "../../feedlist/feedSlice";
import { doListClusters } from "../clusterSlice";
import FeedIcon from "../../../components/FeedIcon";

const mapDispatchToProps = (dispatch) => ({
  openEditPanel(objType, objId) {
    return dispatch(doFetchObjForEdit(objType, objId));
  },
  deleteFeed(id) {
    dispatch(doDeleteObj(id, "feed"));
    return dispatch(doListClusters({ categoryId: "all" }));
  },
});

function SelectedObjCard({ id, str, type, iconUrl, errorCount, lastRetrieved, openEditPanel }) {
  const objType = type === "feed" ? "feed" : "category";
  return (
    <Card variant="outlined">
      <CardContent>
        {type === "feed" ? <FeedIcon iconUrl={iconUrl} /> : null}
        {str}
      </CardContent>
      <CardActions>
        <Button size="small"
          onClick={() => openEditPanel(objType, id)}
      >
          Edit {objType}
        </Button>
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
};

export default connect(null, mapDispatchToProps)(SelectedObjCard);
