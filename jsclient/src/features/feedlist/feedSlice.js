import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";
import { storageGet, storageSet } from "../../storageUtils";


function mergeCategoriesWithUnreads(feedListRows, unreads,
                                    isParentFolded) {
  const categories = [];
  return feedListRows.map((row) => {
     const unread = unreads[row.type + "-" + row.id];
     let index;
     if(row.type === "categ" || row.type === "all-categ") {
       index = categories.length * 3;
       categories.push(row.id);
     } else if (unread) {
       index = categories.indexOf(row["category_id"]) * 3 + 1 / unread;
     } else {
       index = categories.indexOf(row["category_id"]) * 3 + 2;
     }
     return { ...row, unread: unread ? unread : null, index,
              folded: row.folded === undefined ? isParentFolded: row.folded };
  }).sort((row1, row2) => (row1.index - row2.index));
}

const defaultFilter = (row) => !row.folded || row.type === "categ" || row.type === "all-categ";
const feedSlice = createSlice({
  name: "feeds",
  initialState: { loadingFeeds: false,
                  loadingUnreadCounts: false,
                  feedListRows: [],
                  unreads: {},
                  isParentFolded: storageGet("left-menu-folded") === "true",
                  isOpen: storageGet("left-menu-open") !== "false",
                  feedListFilter: defaultFilter,
  },
  reducers: {
    requestedFeeds(state, action) {
      return { ...state, loadingFeeds: true };
    },
    requestedUnreadCounts(state, action) {
      return { ...state, loadingUnreadCounts: true };
    },
    setSearchFilter(state, action) {
      if (!action.payload) {
        return { ...state, feedListFilter: defaultFilter, };
      }
      const feedSearchStr = action.payload.toLowerCase();
      return { ...state,
               feedListFilter: (row) => (
                 row.type !== "categ" && row.type !== "all-categ" && row.str.toLowerCase().includes(feedSearchStr)
               ),
      };
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
    readClusters(state, action) {
      const unreads = { ...state.unreads };
      const readChange = action.payload.action === "unread" ? 1 : -1;
      action.payload.clusters.forEach((cluster) => {
        cluster["feeds_id"].forEach((feedId) => (
          unreads["feed-" + feedId] += readChange
        ));
        if(cluster["categories_id"]) {
          cluster["categories_id"].forEach((catId) => (
            unreads["categ-" + catId] += readChange
          ));
        }
      });
      return { ...state, unreads,
               feedListRows: mergeCategoriesWithUnreads(state.feedListRows,
                                                        unreads,
                                                        state.isParentFolded),
      };
    },
  },
});

export const { requestedFeeds, loadedFeeds,
               requestedUnreadCounts, loadedUnreadCounts,
               toggleMenu, toggleAllFolding, toggleFolding,
               createdObj, setSearchFilter,
               readClusters,
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
    url: apiUrl + "/" + objType + (id ? "/" + id : ""),
    data: obj,
  }, dispatch, getState);
  return result;
};

export const doMarkAllAsRead = (onlySingles): AppThunk => async (dispatch, getState) => {
  const params = { ...getState().clusters.filters };
  if(onlySingles) {
      params["only_singles"] = true;
  }
  // dispatch(requestedMarkAllAsRead({ onlySingles })); // useless for now
  const stringifiedParams = qs.stringify(params);
  const result = await doRetryOnTokenExpiration({
    method: "put",
    url: apiUrl + "/mark-all-as-read?" + stringifiedParams,
  }, dispatch, getState);
  dispatch(loadedUnreadCounts({ unreads: result.data }));
};
