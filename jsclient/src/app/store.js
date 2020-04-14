import { configureStore, Action } from '@reduxjs/toolkit';
import thunk, { ThunkAction }from 'redux-thunk';
import userReducer from '../features/login/userSlice';
import feedsReducer from '../features/feedlist/feedSlice';
import clustersReducer from '../features/clusterlist/clusterSlice';

export default configureStore({
  reducer: {
    login: userReducer,
    feeds: feedsReducer,
    clusters: clustersReducer,
  },
  middleware: [thunk],
});

export type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>
