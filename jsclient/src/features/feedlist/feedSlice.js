import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";

const feedSlice = createSlice({
  name: "feeds",
  initialState: { loading: false,
                  categories: [],
                  isParentFolded: storageGet("left-menu-folded") === "true",
  },
  reducers: {
    askedFeeds(state, action) {
      return { ...state, loading: true };
    },
    toggleFolding(state, action) {
      const newFolding = !state.isParentFolded;
      storageSet("left-menu-folded", newFolding);
      return { ...state, isParentFolded: newFolding };
    },
    loadedFeeds(state, action) {
      const categories = action.payload.categories.map((cat) => (
            { ...cat, isFolded: false }));
      return { ...state, loading: false, categories };
    },
  },
});

export const { askedFeeds, loadedFeeds, toggleFolding } = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (): AppThunk => async (dispatch, getState) => {
  dispatch(askedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/list-feeds",
  }, dispatch, getState);
  dispatch(loadedFeeds({ categories: result.data }));
};
