import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const accessTokenStoragePrefix = 'jarr-';

const loginSlice = createSlice({
  name: 'login',
  initialState: { loading: false, error: undefined,
                  login: localStorage.getItem(accessTokenStoragePrefix + 'login'),
                  password: localStorage.getItem(accessTokenStoragePrefix + 'password'),
                  token: sessionStorage.getItem(accessTokenStoragePrefix + 'token')},
  reducers: {
    attemptLogin(state, action) {
        const { login, password } = action.payload;
        localStorage.setItem(accessTokenStoragePrefix + 'login', login);
        localStorage.setItem(accessTokenStoragePrefix + 'password', password);
        return { ...state, login, password, loading: true };
    },
    loginFailed(state, action) {
        return { ...state, loading: false, token: null,
                 error: action.payload.error };
    },
    tokenAcquired(state, action) {
        sessionStorage.setItem(accessTokenStoragePrefix + 'token',
                               action.payload.data.access_token);
        return { ...state, loading: false,
                 token: action.payload.data.access_token };
    },
    tokenExpire(state, action) {
        sessionStorage.removeItem(accessTokenStoragePrefix + 'token');
        return { ...state, loading: true, token: null};
    },
    logout() {
        localStorage.removeItem(accessTokenStoragePrefix + 'login');
        localStorage.removeItem(accessTokenStoragePrefix + 'password');
        sessionStorage.removeItem(accessTokenStoragePrefix + 'token');
        return { loading: false, error: undefined,
                 login: null, password: null, token: null, };
    }
  }
});

export const { attemptLogin, loginFailed, tokenAcquired, tokenExpire, logout } = loginSlice.actions;

export default loginSlice.reducer;

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
