import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "./const";
import { storageGet, storageSet, storageRemove } from "./storageUtils";
import { authError } from "./features/noauth/noAuthSlice";


const refreshDelay = 10 * 60 * 1000;  // 10 mn in miliseconds

const authSlice = createSlice({
  name: "auth",
  initialState: { login: null,
                  password: null,
                  token: storageGet("token", "session"),
                  refreshedAt: null,
  },
  reducers: {
    attemptLogin: (state, action) => {
      const { login, password } = action.payload;
      return { ...state, login, password };
    },
    loginFailed: (state, action) => ({ token: null, login: null, password: null }),
    tokenAcquired: (state, action) => {
      const token = action.payload.data["access_token"];
      storageSet("token", token, "session");
      return { ...state, token, refreshedAt: new Date().getTime() };
    },
    tokenExpire: (state, action) => {
      storageRemove("token", "session");
      return { ...state, token: null};
    },
    doLogout: () => {
      storageRemove("left-menu-open");
      storageRemove("token", "session");
      return { login: null, password: null, token: null };
    },
  },
});

export const { attemptLogin, loginFailed, tokenAcquired, tokenExpire, doLogout } = authSlice.actions;

export default authSlice.reducer;

export const doRetryOnTokenExpiration = async (payload, dispatch, getState) => {
  const now = new Date();
  const state = getState();
  if (!state.auth.refreshedAt
      || (now.getTime() - state.auth.refreshedAt) > refreshDelay) {
    // token has expired, trying to refresh it
    try {
      const result = await axios({
        method: "get",
        url: `${apiUrl}/auth/refresh`,
        headers: { "Authorization": state.auth.token }
      });
      dispatch(tokenAcquired(result));
      payload.headers = { "Authorization": result.data["access_token"] };
    } catch (err) { // failed to refresh it, logging out
      dispatch(loginFailed());
      dispatch(authError({ statusText: "EXPIRED" }));
      throw err;
    }
  } else {
    payload.headers = { "Authorization": state.auth.token };
  }
  try {
    return await axios(payload);
  } catch (err) {
    // token seems to have expired
    if (err.response && err.response.status === 401
        && err.response.data && err.response.data.message
        && err.response.data.message === "Invalid token, Signature has expired") {
      dispatch(authError({ statusText: "EXPIRED" }));
    } else {
      return err.response;
    }
  }
};
