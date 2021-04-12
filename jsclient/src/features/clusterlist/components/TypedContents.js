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
      body.push(<img key={`i-${article.id}`}
                     src={article.link}
                     alt={article.title} title={article.title} />);
    } else if (type === "audio") {
      if(article.title) {
        body.push(<Typography variant="h6">{article.title}</Typography>);
      }
      body.push(<audio controls key={`v-${article.id}`}>
                  <source src={article.link} />
                </audio>);
    } else if (type === "video") {
      if(article.title) {
        body.push(<Typography variant="h6">{article.title}</Typography>);
      }
      body.push(<video controls key={`a-${article.id}`}>
                  <source src={article.link} />
                </video>);
    }
  });
  return (<Typography hidden={!!hidden} className={classes.article}>
            {body}
          </Typography>);
}

TypedContents.propTypes = {
  type: PropTypes.string.isRequired,
  articles: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string,
    link: PropTypes.string.isRequired,
    "article_type": PropTypes.string.isRequired})),
  hidden: PropTypes.bool.isRequired,
};
