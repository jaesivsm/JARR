import React from "react";
import { createRoot } from "react-dom/client";
import Jarr from "./Jarr";
import store from "./app/store";
import { Provider } from "react-redux";

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <Provider store={store}>
    <Jarr/>
  </Provider>
);
