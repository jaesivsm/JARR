import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Cluster from "./Cluster";
import { doListClusters } from "./clusterSlice";
import clusterListStyle from "./clusterListStyle";

import clsx from "clsx";
function mapStateToProps(state) {
  return { clusters: state.clusters.clusters,
           filters: state.clusters.filters,
           isShifted: state.feeds.isOpen && !state.edit.isOpen,
  };
}

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    return dispatch(doListClusters(filters));
  },
});

function ClusterList({ clusters, filters, listClusters, isShifted }) {
  const classes = clusterListStyle();
  const className = clsx(classes.content, {[classes.contentShift]: isShifted});
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      listClusters(filters);
    }
  }, [everLoaded, filters, listClusters]);
  return (
    <main className={className}>
      {clusters.map((cluster) => (
        <Cluster key={"c-" + cluster.id}
          id={cluster.id}
          mainTitle={cluster.main_title}
          mainFeedTitle={cluster.main_feed_title}
        />
      ))}
    </main>);
}

ClusterList.propTypes = {
    clusters: PropTypes.array.isRequired,
    filters: PropTypes.object.isRequired,
    listClusters: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
