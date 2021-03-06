import { requestedCluster, retrievedCluster } from "../features/clusterlist/slice";
import { doRetryOnTokenExpiration } from "../authSlice";
import { apiUrl } from "../const";

export default (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedCluster({ clusterId }));
  const result = await doRetryOnTokenExpiration({
    method: "get", url: `${apiUrl}/cluster/${clusterId}`,
  }, dispatch, getState);
  dispatch(retrievedCluster({ cluster: result.data }));
};
