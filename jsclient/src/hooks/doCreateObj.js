import { apiUrl } from "../const";
import { doRetryOnTokenExpiration } from "../authSlice";
import doFetchFeeds from "./doFetchFeeds";

export default (type): AppThunk => async (dispatch, getState) => {
  await doRetryOnTokenExpiration({
    method: "post",
    url: `${apiUrl}/${type}`,
    data: getState().edit.loadedObj,
  }, dispatch, getState);
  dispatch(doFetchFeeds());
};
