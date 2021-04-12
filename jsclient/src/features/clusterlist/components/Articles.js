import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";
import ImageIcon from "@material-ui/icons/Image";
import AudioIcon from "@material-ui/icons/MusicNote";
import VideoIcon from "@material-ui/icons/Movie";
import YoutubeIcon from "@material-ui/icons/YouTube";

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
  let index = 0;
  let typedArticles;
  let icon;

  // if no content, and no special type, returning simple article
  if (articles.length === 1
      && (!articleTypes.includes(articles[0].article_type) || !contents)) {
    return <Article article={articles[0]} />;
  }
  if (!!contents && contents.length !== 0) {
    contents.forEach((content) => {
      if (content.type === "youtube") {
        icon = <YoutubeIcon />;
      } else {
        icon = <img src={jarrIcon}
                    alt={proccessedContentTitle}
                    title={proccessedContentTitle} />;
      }
      tabs.push(
        <Tab key={`t-${index}`} value={index}
             icon={icon}
             className={classes.tabs} aria-controls={`a-${index}`}
        />
      );
      pages.push(
        <ProcessedContent key={`pc-${index}`}
                          content={content} hidden={index !== currentIndex} />
      );
      index += 1;
    });
  }
  articleTypes.forEach((type) => {
    typedArticles = articles.filter((article) => article.article_type === type)
          .sort((a1, a2) => (a1.order_in_cluster - a2.order_in_cluster));
    if (type === "image") {
      icon = <ImageIcon />;
    } else if (type === "audio") {
      icon = <AudioIcon />;
    } else if (type === "video") {
      icon = <VideoIcon />;
    }
    if (typedArticles.length !== 0) {
      tabs.push(
        <Tab key={`ta-${type}`} value={index}
             icon={icon}
             className={classes.tabs} aria-controls={`a-${index}`}
        />
      );
      pages.push(
        <TypedContents key={`pc-${index}`}
                       type={type} articles={typedArticles}
                       hidden={index !== currentIndex}
        />
      );
      index += 1;
    }
  });
  articles.forEach((article) => {
    tabs.push(
      <Tab key={`t-${index}`}
        className={classes.tabs}
        icon={<ClusterIcon iconUrl={icons[article["feed_id"]]} />}
        value={index}
        aria-controls={`a-${index}`}
      />);
    pages.push(
      <Article
        key={`a-${index}-${index !== currentIndex ? "h" : ""}`}
        id={`a-${index}`}
        article={article}
        aria-labelledby={`t-${index}`}
        index={index}
        forceShowTitle={true}
        hidden={index !== currentIndex}
      />
    );
    index += 1;
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
  contents: PropTypes.array
};
export default connect(mapStateToProps)(Articles);
