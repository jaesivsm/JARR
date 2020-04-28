import React, { useEffect } from "react";
import { connect } from "react-redux";
import CircularProgress from "@material-ui/core/CircularProgress";
import { doValidOAuth } from "../noAuthSlice";

const mapDispatchToProps = (dispatch) => ({
  validOAuth(code) {
    const url = new URL(window.location.href);
    dispatch(doValidOAuth(url.searchParams.get("code")));
  },
});

function OAuthLogin({ validOAuth }) {
  useEffect(() => validOAuth());
  return <CircularProgress />;
}
export default connect(null, mapDispatchToProps)(OAuthLogin);
