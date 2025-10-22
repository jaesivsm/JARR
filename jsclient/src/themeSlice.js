import { createSlice } from "@reduxjs/toolkit";

// Detect OS theme preference
const getOSThemePreference = () => {
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
};

const themeSlice = createSlice({
  name: "theme",
  initialState: {
    mode: getOSThemePreference(),
  },
  reducers: {
    // Reducer to update theme when OS preference changes
    updateThemeFromOS: (state) => {
      return { ...state, mode: getOSThemePreference() };
    },
  },
});

export const { updateThemeFromOS } = themeSlice.actions;

export default themeSlice.reducer;
