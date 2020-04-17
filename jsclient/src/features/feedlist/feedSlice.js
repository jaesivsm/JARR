import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";

const feedSlice = createSlice({
  name: "feeds",
  initialState: { loading: false,
                  categories: [],
                  isParentFolded: storageGet("left-menu-folded") === "true",
                  isOpen: storageGet("left-menu-open") !== "false",
                  width: 240,
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
    toggleMenu(state, action) {
      const newState = !state.isOpen;
      storageSet("left-menu-open", newState);
      return { ...state, isOpen: newState };
    },
    createdCategory(state, action) {
      action.payload.category.feeds = [];
      state.categories.push(action.payload.category);
      return state;
    },
    createdFeed(state, action) {
      const newFeed = action.payload.feed;
      return { ...state,
               categories: state.categories.map((category) => {
                 if(newFeed["category_id"] === category.id) {

                   return { ...category,
                            feeds: [...category.feeds, newFeed]};
                 }
                 return category;
               }),
      };
    },
  },
});

export const { askedFeeds, loadedFeeds,
               toggleMenu, toggleFolding,
               createdCategory, createdFeed,
} = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (): AppThunk => async (dispatch, getState) => {
  dispatch(askedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/list-feeds",
  }, dispatch, getState);
  dispatch(loadedFeeds({ categories: result.data }));
};

export const doCreateCategory = (category): AppThunk => async (dispatch, getState) => {
  const result = await doRetryOnTokenExpiration({
    method: "post",
    url: apiUrl + "/category?" + qs.stringify(category),
  }, dispatch, getState);
  dispatch(createdCategory({ category: result.data }));
};

export const doCreateFeed = (feed): AppThunk => async (dispatch, getState) => {
  const result = await doRetryOnTokenExpiration({
    method: "post",
    url: apiUrl + "/feed?" + qs.stringify(feed),
  }, dispatch, getState);
  dispatch(createdFeed({ feed: result.data }));
};
