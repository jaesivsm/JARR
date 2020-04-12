import { configureStore, Action } from '@reduxjs/toolkit';
import thunk, { ThunkAction }from 'redux-thunk';
import counterReducer from '../features/counter/counterSlice';
import loginReducer from '../features/login/loginSlice';

export default configureStore({
  reducer: {
    counter: counterReducer,
    login: loginReducer
  },
  middleware: [thunk],
});

export type AppThunk = ThunkAction<void, RootState, unknown, Action<string>>
