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
  const lastRequestRef = useRef(null);
  const isRequestInFlightRef = useRef(false);

  // Keep ref updated
  useEffect(() => {
    clusterIdRef.current = clusterId;
  }, [clusterId]);

  useEffect(() => {
    // Create a unique key for this request
    const requestKey = `${feedId || 'none'}-${categoryId || 'none'}`;

    // Guard 1: Check if already loading (Redux state)
    if (loading) {
      return;
    }

    // Guard 2: Check if this exact request is already in flight (synchronous check)
    if (isRequestInFlightRef.current && lastRequestRef.current === requestKey) {
      return;
    }

    // Guard 3: Check if we just made this exact request
    if (lastRequestRef.current === requestKey) {
      return;
    }

    // Mark request as in flight and store the request key
    isRequestInFlightRef.current = true;
    lastRequestRef.current = requestKey;

    if (feedId) {
      listClusters({ feedId: parseInt(feedId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else if (categoryId) {
      listClusters({ categoryId: categoryId === "all" ? "all" : parseInt(categoryId, 10), clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    } else {
      listClusters({ clusterId: clusterIdRef.current ? parseInt(clusterIdRef.current, 10) : undefined });
    }

    // Reset in-flight flag after a short delay (Redux state should be updated by then)
    setTimeout(() => {
      isRequestInFlightRef.current = false;
    }, 100);

    // Note: 'loading' is intentionally NOT in dependencies to avoid infinite loops
    // The guards above are sufficient to prevent duplicate calls
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
