import { configureStore, Action } from '@reduxjs/toolkit';
import thunk, { ThunkAction }from 'redux-thunk';
import loginReducer from '../features/login/loginSlice';

export default configureStore({
  reducer: {
    login: loginReducer
  },
  middleware: [thunk],
});

export type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>
