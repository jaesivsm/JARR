import React from "react";
import PropTypes from "prop-types";
import { apiUrl } from "../const";
import qs from "qs";
import LinkIcon from "@mui/icons-material/Link";
import { iconStyle } from "./iconStyles";

function ClusterIcon({ iconUrl }) {
  if (iconUrl) {
    return <img style={iconStyle} alt="" src={
          `${apiUrl}/feed/icon?${qs.stringify({ url: iconUrl })}`} />;
  }
  return <LinkIcon sx={iconStyle}
            color="disabled" fontSize="small"/>;
}

ClusterIcon.propTypes = {
  iconUrl: PropTypes.string
};

export default ClusterIcon;
