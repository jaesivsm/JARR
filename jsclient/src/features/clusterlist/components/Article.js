import React from "react";
import PropTypes from "prop-types";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { useTheme } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import Divider from "@material-ui/core/Divider";

import makeStyles from "./style";

function Article({ article, forceShowTitle, hidden }) {
  const classes = makeStyles();
  const theme = useTheme();
  const splitedMode = useMediaQuery(theme.breakpoints.up("md"));
  let title, comments;
  if(forceShowTitle || splitedMode) {
    title = (
      <>
        <Typography variant="h6">{article.title}</Typography>
        <Divider />
      </>
    );
  };
  if (article.comments) {
    comments = (<p><span>Comments</span>
                  <Link color="secondary" target="_blank"
                    key={`ac-${article.id}`} href={article.comments}>
                    {article.comments}
                  </Link></p>);
  }
  return (
    <div hidden={hidden} className={classes.article}>
      {title}
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
          dangerouslySetInnerHTML={{__html: article.content}}
        />
      </div>
    </div>
  );
}

Article.propTypes = {
  article: PropTypes.shape({
    link: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    comments: PropTypes.string,
  }),
  hidden: PropTypes.bool,
  forceShowTitle: PropTypes.bool,
};
Article.defaultProps = {
  hidden: false,
  forceShowTitle: false
};

export default Article;
