import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import CircularProgress from "@material-ui/core/CircularProgress";
// jarr
import { doReadCluster, doUnreadCluster, requestedUnreadCluster } from "./clusterSlice";
import { readClusters } from "../feedlist/feedSlice";

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           loadedCluster: state.clusters.loadedCluster,
           unreadOnClose: !state.clusters.filters.filter,
  };
}

const mapDispatchToProps = (dispatch) => ({
  readCluster(clusterId, feedsId, categoriesId) {
      console.log(clusterId, feedsId, categoriesId);
    dispatch(doReadCluster(clusterId));
    return dispatch(readClusters(
        { clusters: [{ "feeds_id": feedsId,
                       "categories_id": categoriesId }],
          action: "read", }));
  },
  unreadCluster(clusterId, feedsId, categoriesId) {
    dispatch(doUnreadCluster(clusterId));
    return dispatch(readClusters(
        { clusters: [{ "feeds_id": feedsId,
                       "categories_id": categoriesId }],
          action: "unread", }));
  },
  justMarkClusterAsRead(clusterId) {
    return dispatch(requestedUnreadCluster({ clusterId }));
  },
});

function Cluster({ id, feedsId, categoriesId,
                   mainFeedTitle, mainTitle,
                   requestedClusterId, loadedCluster, unreadOnClose,
                   readCluster, unreadCluster, justMarkClusterAsRead }) {
  const expanded = requestedClusterId === id;
  const loaded = !!loadedCluster && loadedCluster.id === id;
  let content;
  if (id === requestedClusterId) {
    if (!loaded) {
      content = <CircularProgress />;
    } else if (loaded) {
      content = (
        <Typography>
          {loadedCluster.articles[0].content}
        </Typography>
      );
    }
  }
  return (
      <ExpansionPanel
        expanded={expanded}
        onChange={() => {
          if (!expanded) {
            readCluster(id, feedsId, categoriesId);
          } else if (unreadOnClose) {
            unreadCluster(id, feedsId, categoriesId);
          } else {
            justMarkClusterAsRead(id);
          }
        }}
      >
        <ExpansionPanelSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          key={"cs-" + id}
        >
          <Link href="/">
           {mainFeedTitle}
          </Link>
          <Typography>
           {mainTitle}
          </Typography>
        </ExpansionPanelSummary>
        <ExpansionPanelDetails key={"cl-" + id}>
          {content}
        </ExpansionPanelDetails>
      </ExpansionPanel>
    );
}

Cluster.propTypes = {
  id: PropTypes.number.isRequired,
  feedsId: PropTypes.array.isRequired,
  categoriesId: PropTypes.array,
  mainTitle: PropTypes.string.isRequired,
  mainFeedTitle: PropTypes.string.isRequired,
  unreadOnClose: PropTypes.bool.isRequired,
  requestedClusterId: PropTypes.number,
  loadedCluster: PropTypes.object,
  readCluster: PropTypes.func.isRequired,
  unreadCluster: PropTypes.func.isRequired,
  justMarkClusterAsRead: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(Cluster);
