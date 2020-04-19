import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../login/userSlice";
import { apiUrl } from "../../const";

const editSlice = createSlice({
  name: "feeds",
  initialState: { isOpen: false,
                  isLoading: false,
                  objType: "", // feed, category
                  objId: null,
                  job: "", // edit, add
                  buildedFeed: null,
                  loadedObj: null,
  },
  reducers: {
    openPanel(state, action) {
      return { ...state, isOpen: true,
               objType: action.payload.objType,
               objId: action.payload.objId,
               job: action.payload.job ? action.payload.job : action.payload.objId ? "edit" : "add",
      };
    },
    closePanel(state, action) {
      return { ...state, isOpen: false,
               objType: "", objId: null, job: "",
               buildedFeed: null, loadedObj: null,
      };
    },
    loadedObjToEdit(state, action) {
      return { ...state, isOpen: true, job: "edit",
               loadedObj: action.payload.data, };
    },
    requestedBuildedFeed(state, action) {
      return { ...state, isLoading: true };
    },
    fetchedBuildedFeed(state, action) {
      return { ...state, isLoading: false,
               buildedFeed: action.payload.buildedFeed };
    },
  },
});

export const { openPanel, closePanel,
               requestedBuildedFeed, fetchedBuildedFeed,
               loadedObjToEdit,
} = editSlice.actions;
export default editSlice.reducer;

export const doBuildFeed = (url): AppThunk => async (dispatch, getState) => {
  dispatch(requestedBuildedFeed());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/feed/build?" + qs.stringify({ url }),
  }, dispatch, getState);
  dispatch(fetchedBuildedFeed({ buildedFeed: result.data }));
};

export const doFetchObjForEdit = (type, id): AppThunk => async (dispatch, getState) => {
  dispatch(openPanel({ job: "loading", objId: id, objType: type, }));
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/" + type + "/" + id,
  }, dispatch, getState);
  return dispatch(loadedObjToEdit({ data: result.data }));
};
