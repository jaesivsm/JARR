import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "./const";
import { storageGet, storageSet, storageRemove } from "./storageUtils";
import { authError } from "./features/noauth/noAuthSlice";

const authSlice = createSlice({
  name: "auth",
  initialState: { login: storageGet("login"),
                  password: storageGet("password"),
                  token: storageGet("token", "session")
  },
  reducers: {
    attemptLogin(state, action) {
      const { login, password } = action.payload;
      storageSet("login", login);
      storageSet("password", password);
      return { ...state, login, password };
    },
    loginFailed(state, action) {
      storageRemove("login");
      storageRemove("password");
      return { token: null, login: null, password: null };
    },
    tokenAcquired(state, action) {
      const token = action.payload.data.access_token;
      storageSet("token", token, "session");
      return { ...state, token };
    },
    tokenExpire(state, action) {
      storageRemove("token", "session");
      return { ...state, token: null};
    },
    doLogout() {
      storageRemove("login");
      storageRemove("password");
      storageRemove("left-menu-open");
      storageRemove("token", "session");
      return { login: null, password: null, token: null };
    }
  }
});

export const { attemptLogin, loginFailed, tokenAcquired, tokenExpire, doLogout } = authSlice.actions;

export default authSlice.reducer;

export const doRetryOnTokenExpiration = async (payload, dispatch, getState) => {
  const state = getState();
  payload.headers = { "Authorization": state.auth.token };
  try {
    return await axios(payload);
  } catch (err) {
      if (err.response && err.response.status === 401
          && err.response.data && err.response.data.message
          && err.response.data.message === "Invalid token, Signature has expired") {
      try {
        const loginResult = await axios.post(apiUrl + "/auth",
            { login: state.auth.login, password: state.auth.password });
        dispatch(tokenAcquired(loginResult));
        payload.headers = { "Authorization": loginResult.data.access_token };
        return await axios(payload);
      } catch (err) {
        dispatch(loginFailed());
        return dispatch(authError(err.response));
      }
    } else {
      return err.response;
    }
  }
};
