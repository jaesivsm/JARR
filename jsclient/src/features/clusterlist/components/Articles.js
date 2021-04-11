import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";

import Article from "./Article";
import {articleTypes, TypedContents} from "./TypedContents";
import ProcessedContent from "./ProcessedContent";
import makeStyles from "./style";
import ClusterIcon from "../../../components/ClusterIcon";
import jarrIcon from "../../../components/JarrIcon.gif";

function mapStateToProps(state) {
  return { icons: state.feeds.icons,
           articles: state.clusters.loadedCluster.articles,
           contents: state.clusters.loadedCluster.contents,
  };
}
const proccessedContentTitle = "proccessed content";

function Articles({ articles, icons, contents }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const classes = makeStyles();

  let tabs = [];
  let pages = [];
  let count = 0;
  let typedArticles;

  // if no content, and no special type, returning simple article
  if (articles.length === 1 && !(articles[0].article_type in articleTypes) && !contents) {
    return <Article article={articles[0]} hidden={false} />;
  }
  if (contents.length !== 0) {
    contents.forEach((content) => {
      tabs.push(
        <Tab key={`t-${count}`}
          className={classes.tabs}
          icon={<img src={jarrIcon}
                     alt={proccessedContentTitle}
                     title={proccessedContentTitle} />}
          label={proccessedContentTitle}
          value={count} aria-controls={`a-${count}`}
        />
      );
      pages.push(
          <ProcessedContent
            content={content}
            hidden={count === currentIndex}
          />
      );
      count += 1;
    });
  }
  articleTypes.forEach((type) => {
    typedArticles = articles.filter((article) => article.article_type === type);
    if (typedArticles.length !== 0) {
      tabs.push(
        <Tab key={`t-${count}`}
          className={classes.tabs}
          icon={<img src={jarrIcon} alt={type} title={type} />}
          label={type}
          value={count} aria-controls={`a-${count}`}
        />
      );
      pages.push(
        <TypedContents
          type={type} articles={typedArticles}
          hidden={count === currentIndex}
        />
      );
      count += 1;
    }
  });
  return (
    <>
      <Tabs indicatorColor="primary" textColor="primary"
        value={currentIndex}
        onChange={(e, v) => setCurrentIndex(v)}>
        {tabs}
      </Tabs>
      {pages}
    </>
  );
}
Articles.propTypes = {
  articles: PropTypes.array,
  contents: PropTypes.arrayOf({
    type: PropTypes.string.isRequired,
    link: PropTypes.string.isRequired,
    comments: PropTypes.string,
    content: PropTypes.string
  }),
};
export default connect(mapStateToProps)(Articles);
