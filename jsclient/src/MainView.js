import React, { useEffect, useRef } from "react";
import { connect } from "react-redux";
import { useParams } from "react-router-dom";
import ClusterList from "./features/clusterlist/ClusterList";
import doListClusters from "./hooks/doListClusters";
import doFetchCluster from "./hooks/doFetchCluster";

const mapStateToProps = (state) => ({
  loading: state.clusters.loading,
});

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    dispatch(doListClusters(filters));
  },
  fetchCluster(clusterId) {
    dispatch(doFetchCluster(clusterId));
  },
});

function MainView({ listClusters, fetchCluster, loading }) {
  const { feedId, categoryId, clusterId } = useParams();
  const clusterIdRef = useRef(clusterId);

  // Keep ref updated
  useEffect(() => {
    clusterIdRef.current = clusterId;
  }, [clusterId]);

  useEffect(() => {
    // Guard: Don't fetch if already loading to prevent duplicate API calls
    if (loading) {
      return;
    }

    if (feedId) {
      listClusters({ feedId: parseInt(feedId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else if (categoryId) {
      listClusters({ categoryId: categoryId === "all" ? "all" : parseInt(categoryId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else {
      listClusters({ clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    }
    // Note: 'loading' is intentionally NOT in dependencies to avoid infinite loops
    // The guard above is sufficient to prevent duplicate calls
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

export default connect(mapStateToProps, mapDispatchToProps)(MainView);
