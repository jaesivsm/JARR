import qs from "qs";
import { apiUrl } from "../const";
import { doRetryOnTokenExpiration } from "../authSlice";
import { loadedUnreadCounts } from "../features/feedlist/slice";

export default (onlySingles): AppThunk => async (dispatch, getState) => {
  const params = { ...getState().clusters.filters };
  if(onlySingles) {
      params["only_singles"] = true;
  }
  // dispatch(requestedMarkAllAsRead({ onlySingles })); // useless for now
  const stringifiedParams = qs.stringify(params);
  const result = await doRetryOnTokenExpiration({
    method: "put",
    url: `${apiUrl}/mark-all-as-read?${stringifiedParams}`,
  }, dispatch, getState);
  dispatch(loadedUnreadCounts({ unreads: result.data }));
};
