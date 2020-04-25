import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";

import makeStyles from "./articleStyle";

function Article({ article, hidden }) {
  const classes = makeStyles();
  return (
    <div className={classes.article}>
      <p>
        <span>Link</span>
        <Link
          key={`al-${article.id}`}
          href={article.link}>
          {article.link}
        </Link>
      </p>
      <p>
        <span>Comments</span>
        <Link
          key={`ac-${article.id}`}
          href={article.comments}>
          {article.comments}
        </Link>
      </p>
      <Typography
        hidden={!!hidden}
        dangerouslySetInnerHTML={{__html: article.content}}
      />
    </div>
  );
}

Article.propTypes = {
  article: PropTypes.object.isRequired,
  hidden: PropTypes.bool.isRequired,
};

export default Article;
