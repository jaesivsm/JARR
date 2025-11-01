import React, { useEffect, useRef } from "react";
import { connect } from "react-redux";
import { useParams } from "react-router-dom";
import ClusterList from "./features/clusterlist/ClusterList";
import doListClusters from "./hooks/doListClusters";
import doFetchCluster from "./hooks/doFetchCluster";

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    dispatch(doListClusters(filters));
  },
  fetchCluster(clusterId) {
    dispatch(doFetchCluster(clusterId));
  },
});

function MainView({ listClusters, fetchCluster }) {
  const { feedId, categoryId, clusterId } = useParams();
  const clusterIdRef = useRef(clusterId);

  // Keep ref updated
  useEffect(() => {
    clusterIdRef.current = clusterId;
  }, [clusterId]);

  useEffect(() => {
    if (feedId) {
      listClusters({ feedId: parseInt(feedId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else if (categoryId) {
      listClusters({ categoryId: categoryId === "all" ? "all" : parseInt(categoryId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else {
      listClusters({ clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [feedId, categoryId]);

  useEffect(() => {
    if (clusterId) {
      fetchCluster(parseInt(clusterId, 10));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clusterId]);

  return <ClusterList />;
}

export default connect(null, mapDispatchToProps)(MainView);
