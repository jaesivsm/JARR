import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import Divider from "@material-ui/core/Divider";

import makeStyles from "./style";

function Content({ content, hidden }) {
  const classes = makeStyles();
  let head, comments, body;
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
  } else if (content.type === "fetched") {
    if (content.comments) {
      comments = (
        <p>
          <span>Comments</span>
          <Link color="secondary" target="_blank" href={content.comments}>
            {content.comments}
          </Link>
        </p>
      );
    }
    head = (
      <p>
        <span>Link</span>
        <Link color="secondary" target="_blank" href={content.link}>
          {content.link}
        </Link>
      </p>
    );
    body = (
      <div className={classes.articleInner}>
        <Typography
          dangerouslySetInnerHTML={{__html: content.content}}
        />
      </div>
    );
  } else if (content.type === "embedded" && content.player === "youtube") {
    body = (
      <div className={classes.videoContainer}>
        <iframe key="jarr-proccessed-content"
          title="JARR processed Player"
          id="ytplayer"
          type="text/html"
          src={`https://www.youtube.com/embed/${content.videoId}`}
          frameBorder="0"
        />
      </div>
    );
  }
  return (
    <div hidden={hidden} className={classes.article}>
      {head}
      {comments}
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
