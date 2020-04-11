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
        console.log(state);
        console.log(action);
        const { login, password } = action.payload;
        return { login, password, loading: true, ...state };
    },
    loginFailed(state, action) {
        return { loading: false, token: undefined,
                 error: action.payload.error, ...state };
    },
    tokenAcquire(state, action) {
        return { loading: false, token: action.payload.token, ...state };
    },
    tokenExpire(state, action) {
        return { loading: true, token: undefined, ...state };
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
