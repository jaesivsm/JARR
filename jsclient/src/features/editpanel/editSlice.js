import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { doRetryOnTokenExpiration } from "../../authSlice";
import { apiUrl } from "../../const";

const editSlice = createSlice({
  name: "feeds",
  initialState: { isOpen: false,
                  isLoading: false,
                  objType: "", // feed, category
                  objId: null,
                  job: "", // edit, add
                  loadedObj: {},
                  editedKeys: [],
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
               loadedObj: {},
               editedKeys: [],
      };
    },
    editLoadedObj(state, action) {
      return { ...state,
               editedKeys: [ ...state.editedKeys, action.payload.key ],
               loadedObj: { ...state.loadedObj,
                            [action.payload.key]: action.payload.value }
      };
    },
    loadedObjToEdit(state, action) {
      if (state.objId !== action.payload.data.id || !action.payload.noIdCheck ) {
        // not the object that was asked for last, ignoring
        return state;
      }
      return { ...state, isOpen: true, job: "edit",
               editedKeys: [],
               loadedObj: action.payload.data, };
    },
    requestedBuildedFeed(state, action) {
      return { ...state, isLoading: true };
    },
  },
});

export const { openPanel, closePanel,
               requestedBuildedFeed,
               editLoadedObj, loadedObjToEdit,
} = editSlice.actions;
export default editSlice.reducer;

export const doBuildFeed = (url): AppThunk => async (dispatch, getState) => {
  dispatch(requestedBuildedFeed());
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/feed/build?" + qs.stringify({ url }),
  }, dispatch, getState);
  dispatch(loadedObjToEdit({ data: result.data, noIdCheck: true }));
};

export const doFetchObjForEdit = (type, id): AppThunk => async (dispatch, getState) => {
  dispatch(openPanel({ job: "load", objId: id, objType: type }));
  const url = apiUrl + "/" + type + (id ? "/" + id : "");
  const result = await doRetryOnTokenExpiration({
    method: "get", url,
  }, dispatch, getState);
  dispatch(loadedObjToEdit({ data: result.data }));
};
