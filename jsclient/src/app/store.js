import { configureStore } from "@reduxjs/toolkit";
import authReducer from "../authSlice";
import noAuthReducer from "../features/noauth/noAuthSlice";
import feedsReducer from "../features/feedlist/slice";
import clustersReducer from "../features/clusterlist/slice";
import editReducer from "../features/editpanel/slice";
import themeReducer from "../themeSlice";

export default configureStore({
  reducer: {
    auth: authReducer,
    noauth: noAuthReducer,
    feeds: feedsReducer,
    clusters: clustersReducer,
    edit: editReducer,
    theme: themeReducer,
  },
});

export type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>;
