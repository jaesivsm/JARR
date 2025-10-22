import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, StyledEngineProvider } from "@mui/material/styles";

import {jarrTheme, jarrLoginTheme} from "./Jarr.theme";
import NoAuth from "./features/noauth/NoAuth";
import TopMenu from "./features/topmenu/TopMenu";
import FeedList from "./features/feedlist/FeedList";
import EditPanel from "./features/editpanel/EditPanel";
import MainView from "./MainView";

function mapStateToProps(state) {
  return { isLogged: !!state.auth.accessToken, };
}

function Jarr({ isLogged, isLeftMenuOpen }) {
  if (!isLogged) {
    return (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <StyledEngineProvider injectFirst>
          <ThemeProvider theme={jarrLoginTheme}>
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
        <ThemeProvider theme={jarrTheme}>
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
};

export default connect(mapStateToProps)(Jarr);
