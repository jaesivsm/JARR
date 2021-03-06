import { apiUrl } from "../const";
import { doRetryOnTokenExpiration } from "../authSlice";
import { requestedFeeds, loadedFeeds } from "../features/feedlist/slice";

export default (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: `${apiUrl}/list-feeds`,
  }, dispatch, getState);
  dispatch(loadedFeeds({ feedListRows: result.data }));
};
