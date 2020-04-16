import { createSlice } from "@reduxjs/toolkit";

const editSlice = createSlice({
  name: "feeds",
  initialState: { isOpen: false,
                  rightPanelObjType: null, // feed, category
                  rightPanelObjId: null,
                  rightPanelJob: null, // edit, add

  },
  reducers: {
    openPanel(state, action) {
      return { ...state, isOpen: true,
               objType: action.payload.objType,
               objId: action.payload.objId,
               job: action.payload.objId ? "edit" : "add",
      };
    },
  },
});

export const { openPanel } = editSlice.actions;
export default editSlice.reducer;
