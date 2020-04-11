import { createSlice } from '@reduxjs/toolkit';

const loginSlice = createSlice({
  name: 'login',
  initialState: { loading: false,
                  error: undefined,
                  login: undefined,
                  password: undefined,
                  token: undefined },
  reducers: {
    login(state, action) {
        const { login, password } = action.payload;
        return { ...state, login, password, loading: true };
    },
    loginFailed(state, action) {
        return { ...state, loading: false, token: undefined,
                 error: action.payload.error };
    },
    tokenAcquire(state, action) {
        return { ...state, loading: false, token: action.payload.token };
    },
    tokenExpire(state, action) {
        return { ...state, loading: true, token: undefined };
    },
    logout() {
        return { loading: false,
                 login: undefined,
                 password: undefined,
                 token: undefined,
                 loginError: undefined};
    }
  }
});

export const { login, loginFailed, tokenAcquire, tokenExpire, logout } = loginSlice.actions;

export default loginSlice.reducer;
