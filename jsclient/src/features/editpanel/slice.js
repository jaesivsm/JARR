import { createSlice } from "@reduxjs/toolkit";

const defaultFilter = { action: "mark as read", "action on": "match",
                        type: "simple match", pattern: "" };

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
    openPanel: (state, action) => ({
      ...state, isOpen: true,
      isLoading: !!action.payload.isLoading,
      objType: action.payload.objType,
      objId: action.payload.objId,
      job: action.payload.job ? action.payload.job : action.payload.objId ? "edit" : "add",
    }),
    closePanel: (state, action) => ({
      ...state, isOpen: false,
      objType: "", objId: null, job: "",
      loadedObj: {},
      editedKeys: [],
    }),
    editLoadedObj: (state, action) => ({
      ...state,
      editedKeys: [ ...state.editedKeys, action.payload.key ],
      loadedObj: { ...state.loadedObj,
                   [action.payload.key]: action.payload.value }
    }),
    loadedObjToEdit: (state, action) => {
      if (state.objId !== action.payload.data.id && !action.payload.noIdCheck ) {
        // not the object that was asked for last, ignoring
        return state;
      }
      const loadedObj = { ...action.payload.data };
      if (loadedObj.filters) {
        loadedObj.filters = loadedObj.filters.map((filter, i) => (
          { id: `f${i}`, ...filter }
        ));
      }
      return { ...state, isOpen: true, isLoading: false,
               editedKeys: [], loadedObj,
               job: action.payload.job ? action.payload.job: state.job };
    },
    requestedBuildedFeed: (state, action) => ({ ...state, isLoading: true }),
    addFilter: (state, action) => {
      let filters = state.loadedObj.filters;
      if (filters) {
        filters = [ ...filters,
                    { ...defaultFilter, id: `f${filters.length + 1}` }];
      } else {
        filters = [ { ...defaultFilter, id: "f1" } ];
      }
      return { ...state,
               editedKeys: [ ...state.editedKeys, "filters"],
               loadedObj: { ...state.loadedObj, filters },
      };
    },
    moveUpFilter: (state, action) => {
      const filters = [ ...state.loadedObj.filters.slice(0, action.payload - 1),
                        state.loadedObj.filters[action.payload],
                        state.loadedObj.filters[action.payload - 1],
                        ...state.loadedObj.filters.slice(action.payload + 1)];
      return { ...state,
               editedKeys: [ ...state.editedKeys, "filters"],
               loadedObj: { ...state.loadedObj, filters },
      };
    },
    moveDownFilter(state, action) {
      const filters = [ ...state.loadedObj.filters.slice(0, action.payload),
                        state.loadedObj.filters[action.payload + 1],
                        state.loadedObj.filters[action.payload],
                        ...state.loadedObj.filters.slice(action.payload + 2)];
      return { ...state,
               editedKeys: [ ...state.editedKeys, "filters"],
               loadedObj: { ...state.loadedObj, filters },
      };
    },
    editFilter: (state, action) => {
      state.loadedObj.filters[action.payload.index][action.payload.key] = action.payload.value;
      if (state.editedKeys.indexOf("filters") === -1) {
        state.editedKeys.push("filters");
      }
      return state;
    },
    removeFilter: (state, action) => ({
      ...state,
      editedKeys: [ ...state.editedKeys, "filters"],
      loadedObj: { ...state.loadedObj,
      filters: [ ...state.loadedObj.filters.slice(0, action.payload),
                 ...state.loadedObj.filters.slice(action.payload + 1)] },
    }),
  },
});

export const { openPanel, closePanel,
               requestedBuildedFeed,
               editLoadedObj, loadedObjToEdit,
               addFilter, moveUpFilter, moveDownFilter, editFilter, removeFilter,
} = editSlice.actions;
export default editSlice.reducer;
