import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import CircularProgress from "@material-ui/core/CircularProgress";
// jarr
import Articles from "./Articles";
import Article from "./Article";

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           loadedCluster: state.clusters.loadedCluster,
           unreadOnClose: !state.clusters.filters.filter,
           icons: state.feeds.icons,
  };
}

function Content({ clusterId, requestedClusterId, loadedCluster, icons }) {
  if (!loadedCluster || !requestedClusterId || !loadedCluster.id
      || clusterId !== requestedClusterId) {
    return null;
  }
  if (loadedCluster.id !== clusterId) {
    return <CircularProgress />;
  } else if (loadedCluster.articles.length === 1) {
    return (<Article article={loadedCluster.articles[0]}
                     hidden={false} />);
  } else {
    return (<Articles articles={loadedCluster.articles}
                      icons={icons} />);
  }
}

Content.propTypes = {
  clusterId: PropTypes.number,
  requestedClusterId: PropTypes.number,
  loadedCluster: PropTypes.object,
};

export default connect(mapStateToProps)(Content);
