import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "../../const";
import { attemptLogin, tokenAcquired, loginFailed } from "../../authSlice";

const noAuthSlice = createSlice({
  name: "noauth",
  initialState: { loading: false,
                  loginError: null,
                  passwordError: null,
                  creationError: null,
  },
  reducers: {
    requestSent(state, action) {
      return { ...state, loading: true };
    },
    responseRecieved(state, action) {
      return { ...state, loading: false };
    },
    authError(state, action) {
      state =  { loading: false,
                 loginError: null,
                 passwordError: null,
                 creationError: null,
      };
      if (action.payload.statusText === "CONFLICT") {
        state.creationError = "Already in use. Please choose another login.";
      } else if (action.payload.statusText === "FORBIDDEN") {
        state.passwordError = "Wrong password.";
      } else if (action.payload.statusText === "NOT FOUND") {
        state.loginError = "User does not exist.";
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
      method: 'post',
      url: apiUrl + '/user',
      data: { login, password, email },
    });
    dispatch(responseRecieved());
    return dispatch(attemptLogin({ login, password }));
  } catch (err) {
    return dispatch(authError(err.response));
  }
}
