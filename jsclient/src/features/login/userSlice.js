import axios from "axios";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "../../const";
import { storageGet, storageSet, storageRemove } from "../../storageUtils";

const userSlice = createSlice({
  name: "user",
  initialState: { loading: false, error: null,
                  login: storageGet("login"),
                  password: storageGet("password"),
                  token: storageGet("token", "session"),
                  isLeftMenuOpen: storageGet("left-menu-open") !== "false",
                  isRightPanelOpen: false,
                  rightPanelObjType: null, // feed, category
                  rightPanelObjId: null,
                  rightPanelJob: null, // edit, add
  },
  reducers: {
    attemptLogin(state, action) {
      const { login, password } = action.payload;
      storageSet("login", login);
      storageSet("password", password);
      return { ...state, login, password, loading: true };
    },
    loginFailed(state, action) {
      storageRemove("login");
      storageRemove("password");
      return { ...state, loading: false,
               token: null, login: null, password: null,
               error: action.payload.error };
    },
    tokenAcquired(state, action) {
      const token = action.payload.data.access_token;
      storageSet("token", token, "session");
      return { ...state, token, loading: false };
    },
    tokenExpire(state, action) {
      storageRemove("token", "session");
      return { ...state, loading: true, token: null};
    },
    toggleLeftMenu(state, action) {
      const newState = !state.isLeftMenuOpen;
      storageSet("left-menu-open", newState);
      return { ...state, isLeftMenuOpen: newState };
    },
    toggleRightPanel(state, action) {
      return { ...state, isRightPanelOpen: true,
               rightPanelObjType: action.payload.objType,
               rightPanelObjId: action.payload.objId,
               rightPanelJob: action.payload.objId ? "edit" : "add",
      };
    },
    doLogout() {
      storageRemove("login");
      storageRemove("password");
      storageRemove("left-menu-open");
      storageRemove("token", "session");
      return { loading: false, error: null,
               login: null, password: null, token: null,
               isLeftMenuOpen: true,
      };
    }
  }
});

export const { attemptLogin, loginFailed, tokenAcquired, tokenExpire, doLogout,
               toggleLeftMenu, toggleRightPanel,
} = userSlice.actions;

export default userSlice.reducer;

export const doLogin = (
  login: string,
  password: string
): AppThunk => async (dispatch) => {
  try {
    dispatch(attemptLogin({ login, password }));
    const result = await axios.post(
        apiUrl + "/auth",
        { login, password },
        { responseType: "json" },
    );
    dispatch(tokenAcquired(result));
  } catch (err) {
    dispatch(loginFailed({ error: err.toString() }));
  }
};

export const doRetryOnTokenExpiration = async (payload, dispatch, getState) => {
  const state = getState();
  payload.headers = { "Authorization": state.login.token };
  try {
    return await axios(payload);
  } catch (err) {
      if (err.response && err.response.status === 401
          && err.response.data && err.response.data.message
          && err.response.data.message === "Invalid token, Signature has expired") {
      try {
        const loginResult = await axios.post(apiUrl + "/auth",
            { login: state.login.login, password: state.login.password });
        dispatch(tokenAcquired(loginResult));
        payload.headers = { "Authorization": loginResult.data.access_token };
        return await axios(payload);
      } catch (err) {
        dispatch(loginFailed({ error: err.toString() }));
      }
    }
  }
};
