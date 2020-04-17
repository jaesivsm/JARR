import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";


function mergeCategoriesWithUnreads(categories, unreads) {
  return categories.map((category) => {
      let catUnreadCount = 0;
      const mergedCategory = { ...category, isFolded: false,
                               feeds: category.feeds.map((feed) => {
                                 const unread = unreads.filter((unread) => {
                                   return unread["feed_id"] === feed.id;
                                 });
                                 const unreadCount = unread && unread[0] ? unread[0].unread : 0;
                                 catUnreadCount += unreadCount;
                                 return { ...feed, unreadCount };
                               }),
      };
      mergedCategory.unreadCount = catUnreadCount;
      return mergedCategory;
  })
}

const feedSlice = createSlice({
  name: "feeds",
  initialState: { loadingFeeds: false,
                  loadingUnreadCounts: false,
                  categories: [],
                  unreads: [],
                  isParentFolded: storageGet("left-menu-folded") === "true",
                  isOpen: storageGet("left-menu-open") !== "false",
  },
  reducers: {
    requestedFeeds(state, action) {
      return { ...state, loadingFeeds: true };
    },
    requestedUnreadCounts(state, action) {
      return { ...state, loadingUnreadCounts: true };
    },
    toggleFolding(state, action) {
      const newFolding = !state.isParentFolded;
      storageSet("left-menu-folded", newFolding);
      return { ...state, isParentFolded: newFolding };
    },
    loadedFeeds(state, action) {
      return { ...state, loadingFeeds: false,
               categories: mergeCategoriesWithUnreads(action.payload.categories,
                                                      state.unreads),
      };
    },
    loadedUnreadCounts(state, action) {
      return { ...state, loadedUnreadCounts: false,
               unreads: action.payload.unreads,
               categories: mergeCategoriesWithUnreads(state.categories,
                                                      action.payload.unreads),
      };
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

export const { requestedFeeds, loadedFeeds,
               requestedUnreadCounts, loadedUnreadCounts,
               toggleMenu, toggleFolding,
               createdCategory, createdFeed,
} = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/list-feeds",
  }, dispatch, getState);
  dispatch(loadedFeeds({ categories: result.data }));
};

export const doFetchUnreadCount = (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedUnreadCounts());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/unreads",
  }, dispatch, getState);
  dispatch(loadedUnreadCounts({ unreads: result.data }));
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
