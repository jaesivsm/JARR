import React from "react";
import ReactDOM from "react-dom";
import Jarr from "./Jarr";
import store from "./app/store";
import { Provider } from "react-redux";

ReactDOM.render(
  <Provider store={store}>
    <Jarr/>
  </Provider>,
  document.getElementById("root")
);
