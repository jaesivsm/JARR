import React, { useEffect } from "react";
import { connect } from "react-redux";
import { doValidOAuth } from "../noAuthSlice";
import { Redirect, useLocation } from "react-router-dom";

const mapDispatchToProps = (dispatch) => ({
  validOAuth(code) {
    dispatch(doValidOAuth(code));
  },
});

function OAuthLogin({ validOAuth }) {
  const query = new URLSearchParams(useLocation().search);
  useEffect(() => validOAuth(query.get("code")));
  return <Redirect to={{pathname: "/", state: { isLoading: true }}} />;
}
export default connect(null, mapDispatchToProps)(OAuthLogin);
