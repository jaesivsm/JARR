import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";


function mergeCategoriesWithUnreads(feedListRows, unreads,
                                    isParentFolded) {
  return feedListRows.map((row) => {
     const unread = unreads[row.type+"-" + row.id];
     return { ...row,  unread: unread ? unread : null,
              folded: row.folded === undefined ? isParentFolded: row.folded };
  });
}

const feedSlice = createSlice({
  name: "feeds",
  initialState: { loadingFeeds: false,
                  loadingUnreadCounts: false,
                  feedListRows: [],
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
    toggleAllFolding(state, action) {
      const newFolding = !state.isParentFolded;
      storageSet("left-menu-folded", newFolding);
      return { ...state,
               feedListRows: state.feedListRows.map((row) => {
                 return { ...row, folded: newFolding, };
               }),
               isParentFolded: newFolding };
    },
    toggleFolding(state, action) {
      return { ...state, feedListRows: state.feedListRows.map((row) => {
          return { ...row, folded: action.payload === row["category_id"] || (row["type"] === "categ" && row.id === action.payload) ? !row.folded : row.folded }
      })};
    },
    loadedFeeds(state, action) {
      return { ...state, loadingFeeds: false,
               feedListRows: mergeCategoriesWithUnreads(action.payload.feedListRows,
                                                        state.unreads,
                                                        state.isParentFolded),
      };
    },
    loadedUnreadCounts(state, action) {
      return { ...state, loadedUnreadCounts: false,
               unreads: action.payload.unreads,
               feedListRows: mergeCategoriesWithUnreads(state.feedListRows,
                                                        state.unreads,
                                                        state.isParentFolded),
      };
    },
    toggleMenu(state, action) {
      const newState = !state.isOpen;
      storageSet("left-menu-open", newState);
      return { ...state, isOpen: newState };
    },
    createdCategory(state, action) {
      const feedListRow = { id: action.payload.category.id,
                            str: action.payload.category.name,
                            unread: 0,
                            type: "categ", };
      state.feedListRows.push(feedListRow);
      return state;
    },
    createdFeed(state, action) {
      const feedListRow = { id: action.payload.feed.id,
                            str: action.payload.feed.name,
                            unread: 0,
                            type: "feed", };
      //FIXME insert at good place
      return { ...state, feedListRows: [ ...state.feedListRows, feedListRow ],
      };
    },
  },
});

export const { requestedFeeds, loadedFeeds,
               requestedUnreadCounts, loadedUnreadCounts,
               toggleMenu, toggleAllFolding, toggleFolding,
               createdCategory, createdFeed,
} = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedFeeds());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/list-feeds",
  }, dispatch, getState);
  dispatch(loadedFeeds({ feedListRows: result.data }));
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
