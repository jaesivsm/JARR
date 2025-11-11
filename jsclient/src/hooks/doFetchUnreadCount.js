import { requestedUnreadCounts, loadedUnreadCounts } from "../features/feedlist/slice";
import { doRetryOnTokenExpiration } from "../authSlice";
import { apiUrl } from "../const";

// Track in-flight requests to prevent duplicates
let inFlightUnreadRequest = false;

const doFetchUnreadCount = (): AppThunk => async (dispatch, getState) => {
  // Check if already loading
  const state = getState();
  if (state.feeds.loadingUnreadCounts) {
    return;
  }

  // Prevent duplicate concurrent requests
  if (inFlightUnreadRequest) {
    return;
  }

  inFlightUnreadRequest = true;
  dispatch(requestedUnreadCounts());

  try {
    const result = await doRetryOnTokenExpiration({
      method: "get",
      url: `${apiUrl}/unreads`,
    }, dispatch, getState);
    dispatch(loadedUnreadCounts({ unreads: result.data }));
  } finally {
    // Always clear the in-flight flag, even if there was an error
    inFlightUnreadRequest = false;
  }
};

export default doFetchUnreadCount;
