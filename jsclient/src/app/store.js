import { configureStore, Action } from "@reduxjs/toolkit";
import thunk, { ThunkAction }from "redux-thunk";
import authReducer from "../authSlice";
import noAuthReducer from "../features/noauth/noAuthSlice";
import feedsReducer from "../features/feedlist/feedSlice";
import clustersReducer from "../features/clusterlist/clusterSlice";
import editReducer from "../features/editpanel/editSlice";

export default configureStore({
  reducer: {
    auth: authReducer,
    noauth: noAuthReducer,
    feeds: feedsReducer,
    clusters: clustersReducer,
    edit: editReducer,
  },
  middleware: [thunk],
});

export type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>;
