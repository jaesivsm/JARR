import React from "react";
import PropTypes from "prop-types";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import Divider from "@material-ui/core/Divider";

import makeStyles from "./style";

function Article({ article, hidden }) {
  const classes = makeStyles();
  let comments;
  if (article.comments) {
    comments = (<p><span>Comments</span>
                  <Link color="secondary" target="_blank"
                    key={`ac-${article.id}`} href={article.comments}>
                    {article.comments}
                  </Link></p>);
  }
  return (
    <div className={classes.article}>
      <p>
        <span>Link</span>
        <Link color="secondary" target="_blank"
          key={`al-${article.id}`} href={article.link}>
          {article.link}
        </Link>
      </p>
      {comments}
      <Divider />
      <div className={classes.articleInner}>
        <Typography
          hidden={!!hidden}
          dangerouslySetInnerHTML={{__html: article.content}}
        />
        </div>
    </div>
  );
}

Article.propTypes = {
  article: PropTypes.shape({
    link: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    comments: PropTypes.string,
  }),
  hidden: PropTypes.bool.isRequired,
};

export default Article;
