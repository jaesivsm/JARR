import { retrievedClustersList, requestedClustersList } from "../features/clusterlist/slice";
import { doRetryOnTokenExpiration } from "../authSlice";
import doFetchUnreadCount from "./doFetchUnreadCount";
import { apiUrl, pageLength } from "../const";

// Track in-flight requests to prevent duplicates
let inFlightRequest = null;

const doListClusters = (filters): AppThunk => async (dispatch, getState) => {
  // Check if already loading
  const state = getState();
  if (state.clusters.loading) {
    return;
  }

  dispatch(requestedClustersList({ filters }));
  const updatedState = getState();
  const requestedFilter = updatedState.clusters.requestedFilter;

  // Prevent duplicate requests with the same filter
  if (inFlightRequest === requestedFilter) {
    return;
  }

  inFlightRequest = requestedFilter;
  // counting expected result length, if different, we will reload feed count
  let expectedCount = null;
  if(!state.clusters.filters.filter) {
    let key = null;
    if(state.clusters.filters["category_id"]) {
      key = `categ-${state.clusters.filters["category_id"]}`;
    } else if (state.clusters.filters["feed_id"]) {
      key = `feed-${state.clusters.filters["feed_id"]}`;
    }
    if (key !== null && state.feeds.unreads.hasOwnProperty(key)) {
      expectedCount = state.feeds.unreads[key];
    } else if (key !== null) {
      expectedCount = 0;
    }
  }
  try {
    const result = await doRetryOnTokenExpiration({
      method: "get",
      url: `${apiUrl}/clusters?${requestedFilter}`,
    }, dispatch, getState);

    dispatch(retrievedClustersList({ requestedFilter, clusters: result.data,
                                     strat: "replace" }));

    // Get fresh state after the async operation
    const finalState = getState();

    if( // if filter allows us to compare
        // (filtering on read or liked would not work)
        expectedCount !== null
        // and that length doesn't match
        && expectedCount !== result.data.length
        // and that length isn't the max length possible for a page
        && result.data.length !== pageLength
        // and not already loading unreads (prevent duplicate calls)
        && !finalState.feeds.loadingUnreadCounts
    ) {
      dispatch(doFetchUnreadCount());
    }
  } finally {
    // Always clear the in-flight request, even if there was an error
    if (inFlightRequest === requestedFilter) {
      inFlightRequest = null;
    }
  }
};

export default doListClusters;
