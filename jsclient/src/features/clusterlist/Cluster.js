import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import CircularProgress from "@material-ui/core/CircularProgress";

import { doReadCluster, doUnreadCluster, requestedUnreadCluster } from "./clusterSlice";

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           loadedCluster: state.clusters.loadedCluster,
           unreadOnClose: !state.clusters.filters.filter,
  };
}

const mapDispatchToProps = (dispatch) => ({
  readCluster(clusterId) {
    return dispatch(doReadCluster(clusterId));
  },
  unreadCluster(clusterId) {
    return dispatch(doUnreadCluster(clusterId));
  },
  justMarkClusterAsRead(clusterId) {
    return dispatch(requestedUnreadCluster(clusterId));
  },
});

function Cluster({ id, mainFeedTitle, mainTitle,
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
            readCluster(id);
          } else if (unreadOnClose) {
            unreadCluster(id);
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
