import React, { useEffect } from "react";
import { connect } from "react-redux";
import { doValidOAuth } from "../noAuthSlice";
import { Navigate, useLocation } from "react-router-dom";

const mapDispatchToProps = (dispatch) => ({
  validOAuth(code) {
    dispatch(doValidOAuth(code));
  },
});

function OAuthLogin({ validOAuth }) {
  const query = new URLSearchParams(useLocation().search);
  useEffect(() => validOAuth(query.get("code")));
  return <Navigate to="/" state={{ isLoading: true }} replace />;
}
export default connect(null, mapDispatchToProps)(OAuthLogin);
