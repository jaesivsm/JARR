import React, { useState } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";

import Article from "./Article";
import Content from "./Content";
import makeStyles from "./style";
import ClusterIcon from "../../../components/ClusterIcon";
import jarrIcon from "../../../components/JarrIcon.gif";

function mapStateToProps(state) {
  return { icons: state.feeds.icons,
           articles: state.clusters.loadedCluster.articles,
           content: state.clusters.loadedCluster.content,
  };
}
const proccessedContentTitle = "proccessed content";

function Articles({ articles, icons, content }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const classes = makeStyles();

  let contentTitle, contentTab;
  if (articles.length === 1 && !content) {
    return <Article article={articles[0]} />;
  } else if (content) {
    contentTitle = (
      <Tab key="t-0" label=""
        className={classes.tabs}
        icon={<img src={jarrIcon} alt={proccessedContentTitle}
                   title={proccessedContentTitle} />}
        value={0} aria-controls="a-0"
      />
    );
    contentTab = <Content content={content} hidden={0 !== currentIndex} />;
  }
  return (
    <>
      <Tabs indicatorColor="primary" textColor="primary"
        value={currentIndex}
        onChange={(e, v) => setCurrentIndex(v)}>
        {contentTitle}
        {articles.map((article, index) => {
          index = content ? index + 1 : index;
          return (<Tab key={`t-${index}`} label=""
                       className={classes.tabs}
                       icon={<ClusterIcon iconUrl={icons[article["feed_id"]]} />}
                       value={index}
                       aria-controls={`a-${index}`}
                  />);
        })}
      </Tabs>
      {contentTab}
      {articles.map((article, index) => {
        index = content ? index + 1 : index;
        return (
          <Article showTitle
            key={`a-${index}-${index !== currentIndex ? "h" : ""}`}
            id={`a-${index}`}
            article={article}
            aria-labelledby={`t-${index}`}
            index={index}
            hidden={index !== currentIndex}
          />
        );
      })}
    </>
  );
}
Articles.propTypes = {
  articles: PropTypes.array,
  content: PropTypes.shape({
    type: PropTypes.string.isRequired,
    alt: PropTypes.string,
    src: PropTypes.string,
    videoId: PropTypes.string,
    player: PropTypes.string,
  }),
};
export default connect(mapStateToProps)(Articles);
