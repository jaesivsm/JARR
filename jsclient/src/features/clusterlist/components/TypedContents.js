import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";

import makeStyles from "./style";

export const articleTypes = ["image", "audio", "video"];

export function TypedContents({ type, articles, hidden }) {
  const classes = makeStyles();
  let body = [];
  let processed = [];
  if (articles.length === 0) { return ; }
  articles.forEach((article) => {
    if(processed.includes(article.link)) {
      return ;
    }
    processed.push(article.link);
    if (type === "image") {
      body.push(<img key={`i-${article.link}`}
                     src={article.link}
                     alt={article.title} title={article.title} />);
    } else if (type === "audio") {
      body.push(<audio controls key={`v-${article.link}`}>
                  <source src={article.link} />
                </audio>);
    } else if (type === "video") {
      body.push(<video controls key={`a-${article.link}`}>
                  <source src={article.link} />
                </video>);
    }
  });

  return (
    <div hidden={hidden} className={classes.article}>
      <Typography hidden={!!hidden}>
        {body}
      </Typography>
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