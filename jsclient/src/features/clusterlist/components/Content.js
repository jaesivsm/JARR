import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import Divider from "@material-ui/core/Divider";

import makeStyles from "./style";

function Content({ content, hidden }) {
  const classes = makeStyles();
  let head, body;
  if (content.type === "image") {
    head = (
      <p>
        <span>Link</span>
        <Link color="secondary" target="_blank" href={content.src}>
          {content.src}
        </Link>
      </p>
    );
    body = (
      <Typography hidden={!!hidden}>
        <img src={content.src} alt={content.alt} title={content.alt} />
      </Typography>
    );
  }
  return (
    <div hidden={hidden} className={classes.article}>
      {head}
      <Divider />
      {body}
    </div>
  );
}

Content.propTypes = {
  content: PropTypes.shape({
    type: PropTypes.string.isRequired,
    alt: PropTypes.string,
    src: PropTypes.string,
    player: PropTypes.string,
    videoId: PropTypes.string,
  }),
  hidden: PropTypes.bool.isRequired,
};

export default Content;
