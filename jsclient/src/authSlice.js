import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "./const";
import { storageGet, storageSet, storageRemove } from "./storageUtils";
import { authError } from "./features/noauth/noAuthSlice";


const refreshDelay = 10 * 60 * 1000;  // 10 mn in miliseconds

const authSlice = createSlice({
  name: "auth",
  initialState: { accessToken: null,
                  refreshToken: storageGet("refreshToken", "local"),
                  refreshedAt: null,
  },
  reducers: {
    loginFailed: (state, action) => ({ accessToken: null, refreshToken: null }),
    tokenAcquired: (state, action) => {
      const accessToken = action.payload.data["access_token"];
      const refreshToken = action.payload.data["refresh_token"];
      if (!!refreshToken) {
        storageSet("refreshToken", refreshToken, "local");
        return { ...state, accessToken, refreshedAt: new Date().getTime() };
      } else {
        return { ...state, accessToken, refreshToken, refreshedAt: new Date().getTime() };
      }
    },
    tokenExpire: (state, action) => {
      storageRemove("refreshToken", "local");
      return { ...state, accessToken: null, refreshToken: null};
    },
    doLogout: () => {
      storageRemove("left-menu-open", "local");
      storageRemove("refreshToken", "local");
      return { accessToken: null, refreshToken: null };
    },
  },
});

export const { loginFailed, tokenAcquired, tokenExpire, doLogout } = authSlice.actions;

export default authSlice.reducer;

export const doRetryOnTokenExpiration = async (payload, dispatch, getState) => {
  const now = new Date();
  const state = getState();
  if (!state.auth.refreshedAt
      || (now.getTime() - state.auth.refreshedAt) > refreshDelay) {
    // token has expired, trying to refresh it
    try {
      const result = await axios({
        method: "post",
        url: `${apiUrl}/auth/refresh`,
        headers: { "Authorization": state.auth.refreshToken }
      });
      dispatch(tokenAcquired(result));
      payload.headers = { "Authorization": result.data["access_token"] };
    } catch (err) { // failed to refresh it, logging out
      dispatch(loginFailed());
      dispatch(authError({ statusText: "EXPIRED" }));
      throw err;
    }
  } else {
    payload.headers = { "Authorization": state.auth.accessToken };
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
