import { requestedCluster, retrievedCluster } from "../features/clusterlist/slice";
import { doRetryOnTokenExpiration } from "../authSlice";
import { apiUrl } from "../const";

// Track in-flight requests to prevent duplicates
let inFlightClusterRequest = null;

const doFetchCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  const state = getState();

  // Check if we're already fetching this cluster
  if (state.clusters.requestedClusterId === clusterId && inFlightClusterRequest === clusterId) {
    return;
  }

  // Check if this cluster is already loaded and no different cluster is being requested
  if (state.clusters.loadedCluster.id === clusterId && state.clusters.requestedClusterId === clusterId) {
    return;
  }

  // Prevent duplicate requests for the same cluster
  if (inFlightClusterRequest === clusterId) {
    return;
  }

  inFlightClusterRequest = clusterId;
  dispatch(requestedCluster({ clusterId }));

  try {
    const result = await doRetryOnTokenExpiration({
      method: "get", url: `${apiUrl}/cluster/${clusterId}`,
    }, dispatch, getState);
    dispatch(retrievedCluster({ cluster: result.data }));
  } finally {
    // Clear in-flight tracker
    if (inFlightClusterRequest === clusterId) {
      inFlightClusterRequest = null;
    }
  }
};

export default doFetchCluster;
