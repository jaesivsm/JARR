import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "../../const";
import { attemptLogin, tokenAcquired, loginFailed } from "../../authSlice";

const INITIAL_STATE = { loading: false,
                        loginError: null,
                        passwordError: null,
                        creationError: null,
                        recovery: null,
};

const noAuthSlice = createSlice({
  name: "noauth",
  initialState: { ...INITIAL_STATE },
  reducers: {
    requestSent(state, action) {
      return { ...state, loading: true };
    },
    responseRecieved(state, action) {
      return { ...INITIAL_STATE, ...action.payload };
    },
    authError(state, action) {
      state = { ...INITIAL_STATE };
      if (action.payload.statusText === "CONFLICT") {
        state.creationError = "Already in use. Please choose another login.";
      } else if (action.payload.statusText === "FORBIDDEN") {
        state.passwordError = "Wrong password.";
      } else if (action.payload.statusText === "NOT FOUND") {
        state.loginError = "User does not exist.";
      } else if (action.payload.statusText === "EXPIRED") {
        state.loginError = "Your session has expired, please log in again";
      } else {
        state.loginError = "Unknown error.";
        state.creationError = "Unknown error.";
      }
      return state;
    },
    alreadyExistingUser(state, action) {
      return { ...state, loading: false };
    },
  }
});

export const { requestSent, responseRecieved,
               alreadyExistingUser, authError,
} = noAuthSlice.actions;

export default noAuthSlice.reducer;

export const doLogin = (
  login: string,
  password: string
): AppThunk => async (dispatch) => {
  dispatch(requestSent());
  dispatch(attemptLogin({ login, password }));
  try {
    const result = await axios.post(
        apiUrl + "/auth",
        { login, password },
        { responseType: "json" },
    );
    dispatch(responseRecieved());
    dispatch(tokenAcquired(result));
  } catch (err) {
    dispatch(loginFailed());
    return dispatch(authError(err.response));
  }
};

export const doSignUp = (
  login: string,
  password: string,
  email: string,
): AppThunk => async (dispatch) => {
  dispatch(requestSent());
  try {
    await axios({
      method: "post",
      url: apiUrl + "/user",
      data: { login, password, email },
    });
    dispatch(responseRecieved());
    return dispatch(attemptLogin({ login, password }));
  } catch (err) {
    return dispatch(authError(err.response));
  }
};

export const doInitRecovery = (
  login: string,
  email: string,
): AppThunk => async (dispatch) => {
  dispatch(requestSent());
  try {
    const result = await axios({
      method: "post",
      url: apiUrl + "/auth/recovery",
      data: { login, email },
    });
    return dispatch(responseRecieved({ recovery: result }));
  } catch (err) {
    return dispatch(responseRecieved({ recovery: err.response }));
  }
};

export const doRecovery = (
  login: string,
  email: string,
  token: string,
  password: string
): AppThunk => async (dispatch) => {
  dispatch(requestSent());
  try {
    await axios({
      method: "put",
      url: apiUrl + "/auth/recovery",
      data: { login, email, token, password },
    });
    dispatch(responseRecieved());
    return dispatch(attemptLogin({ login, password }));
  } catch (err) {
    return dispatch(responseRecieved({ recovery: err.response }));
  }
};

export const doValidOAuth = (code): AppThunk => async (dispatch) => {
  try {
    dispatch(requestSent());
    const result = await axios({
      method: "post",
      url: apiUrl + "/oauth/callback/google",
      data: { code },
    });
    dispatch(responseRecieved());
    dispatch(tokenAcquired(result));
  } catch (err) {
    dispatch(authError(err.response));
  }
};
