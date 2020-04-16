import { createSlice } from "@reduxjs/toolkit";

const editSlice = createSlice({
  name: "feeds",
  initialState: { isOpen: false,
                  objType: null, // feed, category
                  objId: null,
                  job: null, // edit, add

  },
  reducers: {
    openPanel(state, action) {
      return { ...state, isOpen: true,
               objType: action.payload.objType,
               objId: action.payload.objId,
               job: action.payload.objId ? "edit" : "add",
      };
    },
    closePanel(state, action) {
      return { ...state, isOpen: false,
               objType: null, objId: null, job: null,
      };
    },
  },
});

export const { openPanel, closePanel } = editSlice.actions;
export default editSlice.reducer;
