import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";


function mergeCategoriesWithUnreads(feedListRows, unreads,
                                    isParentFolded) {
  return feedListRows.map((row) => {
     const unread = unreads[row.type + "-" + row.id];
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
          return { ...row, folded: action.payload === row["category_id"] || (row["type"] === "categ" && row.id === action.payload) ? !row.folded : row.folded };
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
                                                        action.payload.unreads,
                                                        state.isParentFolded),
      };
    },
    toggleMenu(state, action) {
      const newState = !state.isOpen;
      storageSet("left-menu-open", newState);
      return { ...state, isOpen: newState };
    },
    createdObj(state, action) {
      const feedListRow = { unread: 0, id: action.payload.data.id };
      if(action.payload.type === "category") {
        feedListRow.str = action.payload.data.name;
        feedListRow.type = "categ";
        state.feedListRows.push(feedListRow);
      } else {
        feedListRow.str = action.payload.data.title;
        feedListRow.type = "feed";
        state.feedListRows.push(feedListRow);
      }
      //FIXME insert at good place
      return { ...state, feedListRows: [ ...state.feedListRows, feedListRow ], };
    },
  },
});

export const { requestedFeeds, loadedFeeds,
               requestedUnreadCounts, loadedUnreadCounts,
               toggleMenu, toggleAllFolding, toggleFolding,
               createdObj,
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

export const doCreateObj = (obj, type): AppThunk => async (dispatch, getState) => {
  const result = await doRetryOnTokenExpiration({
    method: "post",
    url: apiUrl + "/" + type + "?" + qs.stringify(obj),
  }, dispatch, getState);
  dispatch(createdObj({ obj: result.data, type }));
};

export const doEditObj = (id, obj, objType): AppThunk => async (dispatch, getState) => {
  const result = await doRetryOnTokenExpiration({
    method: "put",
    url: apiUrl + "/" + objType + "/" + id,
    data: obj,
  }, dispatch, getState);
  return result;
};
