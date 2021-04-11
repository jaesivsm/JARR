import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";

import makeStyles from "./style";

export const articleTypes = ["image", "audio", "video"];

export function TypedContents({ type, articles, hidden }) {
  const classes = makeStyles();
  let body;
  if (articles.length === 0) { return ; }
  if (type === "image") {
    body = (
      <Typography hidden={!!hidden}>
        {articles.map((article) =>
            <img key={`i-${article.link}`}
                 src={article.link} alt={article.title} title={article.title} />)}
      </Typography>
    );
  } else if (type === "audio") {
    body = (
      <Typography hidden={!!hidden}>
        {articles.map((article) =>
          <audio controls key={`v-${article.link}`}>
            <source src={article.link} />
          </audio>)}
      </Typography>
    );
  } else if (type === "video") {
    body = (
      <Typography hidden={!!hidden}>
        {articles.map((article) =>
          <video controls key={`a-${article.link}`}>
            <source src={article.link} />
          </video>)}
      </Typography>
    );
  }
  return (
    <div hidden={hidden} className={classes.article}>
      {body}
    </div>
  );
}

TypedContents.propTypes = {
  type: PropTypes.string.isRequired,
  articles: PropTypes.arrayOf(PropTypes.shape({
    link: PropTypes.string.isRequired,
    "article_type": PropTypes.string.isRequired})),
  hidden: PropTypes.bool.isRequired,
};
