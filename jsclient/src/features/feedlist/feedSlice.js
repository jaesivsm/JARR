import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";

const feedSlice = createSlice({
  name: "feed",
  initialState: { loading: false,
                  categories: [],
  },
  reducers: {
    askedFeeds(state, action) {
      return { ...state, loading: true };
    },
    loadedFeeds(state, action) {
      const categories = action.payload.categories.map((cat) => (
            { ...cat, isFolded: false }));
      return { ...state, loading: false, categories };
    },
  },
});

export const { askedFeeds, loadedFeeds } = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (): AppThunk => async (dispatch, getState) => {
  dispatch(askedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/list-feeds",
  }, dispatch, getState);
  dispatch(loadedFeeds({ categories: result.data }));
};
