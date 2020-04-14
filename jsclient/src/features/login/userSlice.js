import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';
import { storageGet, storageSet, storageRemove } from './storageUtils';

const userSlice = createSlice({
  name: 'user',
  initialState: { loading: false, error: undefined,
                  login: storageGet('login'),
                  password: storageGet('password'),
                  token: storageGet('token', 'session'),
                  isLeftMenuOpen: storageGet('left-menu-open') !== 'false',
                  isLeftMenuFolded: storageGet('left-menu-folded') === 'true',
  },
  reducers: {
    attemptLogin(state, action) {
        const { login, password } = action.payload;
        storageSet('login', login)
        storageSet('password', password)
        return { ...state, login, password, loading: true };
    },
    loginFailed(state, action) {
        return { ...state, loading: false, token: null,
                 error: action.payload.error };
    },
    tokenAcquired(state, action) {
        const token = action.payload.data.access_token;
        storageSet('token', token, 'session');
        return { ...state, token, loading: false };
    },
    tokenExpire(state, action) {
        storageRemove('token', 'session');
        return { ...state, loading: true, token: null};
    },
    toggleFolding(state, action) {
        const newFolding = !state.isLeftMenuFolded;
        storageSet('left-menu-folded', newFolding);
        return { ...state, isLeftMenuFolded: newFolding };
    },
    toggleLeftMenu(state, action) {
        const newState = !state.isLeftMenuOpen;
        storageSet('left-menu-open', newState);
        return { ...state, isLeftMenuOpen: newState};
    },
    logout() {
        storageRemove('login');
        storageRemove('password');
        storageRemove('left-menu-open');
        storageRemove('left-menu-folded');
        storageRemove('token', 'session');
        return { loading: false, error: undefined,
                 login: null, password: null, token: null,
                 isLeftMenuOpen: true,
        };
    }
  }
});

export const { attemptLogin, loginFailed, tokenAcquired, tokenExpire, logout,
               toggleLeftMenu, toggleFolding,
} = userSlice.actions;

export default userSlice.reducer;

export const doLogin = (
  login: string,
  password: string
): AppThunk => async dispatch => {
  try {
    dispatch(attemptLogin({ login, password }));
    const result = await axios.post(
        apiUrl + '/auth',
        { login, password },
        { responseType: 'json' },
    );
    dispatch(tokenAcquired(result))
  } catch (err) {
    dispatch(loginFailed({ error: err.toString() }))
  }
}