import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, StyledEngineProvider } from "@mui/material/styles";

import {jarrTheme, jarrLoginTheme, jarrDarkTheme, jarrLoginDarkTheme} from "./Jarr.theme";
import { updateThemeFromOS } from "./themeSlice";
import NoAuth from "./features/noauth/NoAuth";
import TopMenu from "./features/topmenu/TopMenu";
import FeedList from "./features/feedlist/FeedList";
import EditPanel from "./features/editpanel/EditPanel";
import MainView from "./MainView";

function mapStateToProps(state) {
  return {
    isLogged: !!state.auth.accessToken,
    themeMode: state.theme?.mode || "light",
  };
}

const mapDispatchToProps = (dispatch) => ({
  updateTheme() {
    dispatch(updateThemeFromOS());
  },
});

function Jarr({ isLogged, isLeftMenuOpen, themeMode, updateTheme }) {
  const loginTheme = themeMode === "dark" ? jarrLoginDarkTheme : jarrLoginTheme;
  const mainTheme = themeMode === "dark" ? jarrDarkTheme : jarrTheme;

  // Listen for OS theme preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleThemeChange = (e) => {
      updateTheme();
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleThemeChange);
      return () => mediaQuery.removeEventListener("change", handleThemeChange);
    } else if (mediaQuery.addListener) {
      // Legacy browsers
      mediaQuery.addListener(handleThemeChange);
      return () => mediaQuery.removeListener(handleThemeChange);
    }
  }, [updateTheme]);

  if (!isLogged) {
    return (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <StyledEngineProvider injectFirst>
          <ThemeProvider theme={loginTheme}>
            <div style={{ display: "flex" }}>
              <CssBaseline />
              <NoAuth />
            </div>
          </ThemeProvider>
        </StyledEngineProvider>
      </BrowserRouter>
    );
  }
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <StyledEngineProvider injectFirst>
        <ThemeProvider theme={mainTheme}>
          <div style={{ display: "flex" }}>
            <CssBaseline />
            <TopMenu />
            <FeedList />
            <Routes>
              <Route path="/feed/:feedId/cluster/:clusterId" element={<MainView />} />
              <Route path="/feed/:feedId" element={<MainView />} />
              <Route path="/category/:categoryId/cluster/:clusterId" element={<MainView />} />
              <Route path="/category/:categoryId" element={<MainView />} />
              <Route path="/cluster/:clusterId" element={<MainView />} />
              <Route path="/" element={<MainView />} />
            </Routes>
            <EditPanel />
          </div>
        </ThemeProvider>
      </StyledEngineProvider>
    </BrowserRouter>
  );
}

Jarr.propTypes = {
  isLogged: PropTypes.bool.isRequired,
  themeMode: PropTypes.string.isRequired,
  updateTheme: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(Jarr);
