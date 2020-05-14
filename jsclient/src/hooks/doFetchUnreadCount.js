import { requestedUnreadCounts, loadedUnreadCounts } from "../features/feedlist/slice";
import { doRetryOnTokenExpiration } from "../authSlice";
import { apiUrl } from "../const";

export default (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedUnreadCounts());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: `${apiUrl}/unreads`,
  }, dispatch, getState);
  dispatch(loadedUnreadCounts({ unreads: result.data }));
};
