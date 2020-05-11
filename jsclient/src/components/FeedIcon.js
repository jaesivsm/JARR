import React from "react";
import PropTypes from "prop-types";
import { apiUrl } from "../const";
import qs from "qs";
import LinkIcon from "@material-ui/icons/Link";
import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

const iconStyle = makeStyles((theme: Theme) =>
  createStyles({
    feedIcon: {
      maxWidth: 16,
      maxHeight: 16,
      margin: "8px 5px 8px 20px",
      width: "100%",
      height: "auto",
    }
  }),
);

function FeedIcon({ iconUrl }) {
  const classes = iconStyle();
  if (iconUrl) {
    return <img className={classes.feedIcon} alt=""
            src={`${apiUrl}/feed/icon?${qs.stringify({ url: iconUrl })}`} />;
  }
  return <LinkIcon className={classes.feedIcon}
            color="disabled" fontSize="small"/>;
}

FeedIcon.propTypes = {
  iconUrl: PropTypes.string
};

export default FeedIcon;
