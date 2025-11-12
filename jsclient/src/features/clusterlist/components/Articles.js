import React, { useState, useCallback, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { useParams, useNavigate } from "react-router-dom";

import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import ImageIcon from "@mui/icons-material/Image";
import AudioIcon from "@mui/icons-material/MusicNote";
import VideoIcon from "@mui/icons-material/Movie";
import YoutubeIcon from "@mui/icons-material/YouTube";

import Article from "./Article";
import {articleTypes, TypedContents} from "./TypedContents";
import ProcessedContent from "./ProcessedContent";
import useStyles from "./style";
import ClusterIcon from "../../../components/ClusterIcon";
import jarrIcon from "../../../components/JarrIcon.gif";
import { showCluster, clearSkipToNextMedia, clearForceAutoplay } from "../slice";
import doFetchCluster from "../../../hooks/doFetchCluster";

function mapStateToProps(state) {
  return { icons: state.feeds.icons,
           articles: state.clusters.loadedCluster.articles,
           contents: state.clusters.loadedCluster.contents,
           feedTitle: state.clusters.loadedCluster.main_feed_title,
           autoplayChain: state.clusters.autoplayChain,
           clusters: state.clusters.clusters,
           currentClusterId: state.clusters.requestedClusterId,
           filter: state.clusters.filters.filter,
           skipToNextMediaRequested: state.clusters.skipToNextMediaRequested,
           forceAutoplayNextMedia: state.clusters.forceAutoplayNextMedia,
  };
}

const mapDispatchToProps = (dispatch) => ({
  fetchCluster(clusterId) {
    dispatch(doFetchCluster(clusterId));
  },
  clearSkipRequest() {
    dispatch(clearSkipToNextMedia());
  },
  clearForceAutoplayFlag() {
    dispatch(clearForceAutoplay());
  },
});

const proccessedContentTitle = "proccessed content";

function Articles({ articles, icons, contents, feedTitle, autoplayChain, clusters, currentClusterId, filter, fetchCluster, skipToNextMediaRequested, forceAutoplayNextMedia, clearSkipRequest, clearForceAutoplayFlag }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const classes = useStyles();
  const { feedId, categoryId } = useParams();
  const navigate = useNavigate();

  // Determine if autoplay should be enabled: either chain is on OR manual skip was triggered
  const shouldAutoplay = autoplayChain || forceAutoplayNextMedia;

  // Clear the force autoplay flag after cluster changes (track cluster ID changes)
  useEffect(() => {
    if (forceAutoplayNextMedia && currentClusterId) {
      // Delay clearing to ensure media components have fully mounted and received the autoplay prop
      // This gives time for YouTube player initialization and native media element creation
      const timeout = setTimeout(() => {
        clearForceAutoplayFlag();
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [forceAutoplayNextMedia, currentClusterId, clearForceAutoplayFlag]);

  // Function to find next cluster with media content (going up, to more recent)
  // Respects current filter: "all" shows all, undefined/empty shows unread only, "liked" shows liked only
  const findNextMediaCluster = useCallback(() => {
    if (!clusters || clusters.length === 0) return null;

    const currentIdx = clusters.findIndex(c => c.id === currentClusterId);
    if (currentIdx === -1) return null;

    // Look for the previous cluster (more recent, going up) that matches the current filter
    for (let i = currentIdx - 1; i >= 0; i--) {
      const nextCluster = clusters[i];
      // Check if this cluster should be shown according to the current filter
      // Pass null for requestedClusterId since we want to find the next eligible cluster
      if (showCluster(nextCluster, null, filter)) {
        return nextCluster.id;
      }
    }
    return null;
  }, [clusters, currentClusterId, filter]);

  const skipToNext = useCallback(() => {
    const nextClusterId = findNextMediaCluster();
    if (nextClusterId) {
      // Fetch the cluster data directly first
      fetchCluster(nextClusterId);

      // Update the URL using React Router's navigate
      // This ensures consistency with media player URL updates
      let newUrl;
      if (feedId) {
        newUrl = `/feed/${feedId}/cluster/${nextClusterId}`;
      } else if (categoryId) {
        newUrl = `/category/${categoryId}/cluster/${nextClusterId}`;
      } else {
        newUrl = `/cluster/${nextClusterId}`;
      }
      navigate(newUrl, { replace: true });
    }
  }, [findNextMediaCluster, fetchCluster, feedId, categoryId, navigate]);

  const handleMediaEnded = useCallback(() => {
    if (!autoplayChain) return;
    skipToNext();
  }, [autoplayChain, skipToNext]);

  // Watch for manual skip requests from the UI
  useEffect(() => {
    if (skipToNextMediaRequested) {
      skipToNext();
      clearSkipRequest();
    }
  }, [skipToNextMediaRequested, skipToNext, clearSkipRequest]);

  // Guard against undefined articles
  if (!articles || articles.length === 0) {
    return null;
  }

  const hasProcessedContent = !!contents && contents.length > 0;
  const allArticlesAreTyped = articles.reduce(
    (allTyped, art) => !!(allTyped && articleTypes.includes(art["article_type"])), true);
  // if no content, and no special type, returning simple article
  if (articles.length === 1 && !allArticlesAreTyped && !hasProcessedContent) {
    return <Article article={articles[0]} />;
  }

  let tabs = [];
  let pages = [];
  let index = 0;
  let typedArticles;
  let icon;
  const pushProcessedContent = (content) => {
    if (content.type === "youtube") {
      icon = <YoutubeIcon />;
    } else {
      icon = <img src={jarrIcon}
                  alt={proccessedContentTitle}
                  title={proccessedContentTitle} />;
    }
    tabs.push(<Tab key={`t-${index}`} value={index} icon={icon}
                   className={classes.tabs} aria-controls={`a-${index}`} />);
    pages.push(<ProcessedContent key={`pc-${index}`} content={content}
                                 hidden={index !== currentIndex}
                                 onMediaEnded={handleMediaEnded}
                                 autoplay={shouldAutoplay} />);
    index += 1;
  }
  const pushTypedArticles = (type) => {
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
      const feedIconUrl = typedArticles[0]?.feed_id ? icons[typedArticles[0].feed_id] : null;
      tabs.push(<Tab key={`ta-${type}`} value={index} icon={icon}
                     className={classes.tabs} aria-controls={`a-${index}`} />);
      pages.push(<TypedContents key={`pc-${index}`} type={type}
                                articles={typedArticles}
                                hidden={index !== currentIndex}
                                feedTitle={feedTitle}
                                feedIconUrl={feedIconUrl}
                                onMediaEnded={handleMediaEnded}
                                autoplay={shouldAutoplay} />);
      index += 1;
    }
  }
  const pushClassicArticle = (article) => {
    tabs.push(
      <Tab key={`t-${article.id}`} className={classes.tabs}
           icon={<ClusterIcon iconUrl={icons[article["feed_id"]]} />}
           value={index} aria-controls={`a-${index}`} />);
    pages.push(
      <Article key={`a-${article.id}-${index !== currentIndex ? "h" : ""}`}
               article={article} index={index} aria-labelledby={`t-${index}`}
               forceShowTitle={true} hidden={index !== currentIndex} />);
    index += 1;
  }

  if (hasProcessedContent) {
    contents.forEach(pushProcessedContent);
  }
  // if all articles are typed, pushing typed content formatter first
  if(allArticlesAreTyped) {
    articleTypes.forEach(pushTypedArticles);
    articles.forEach(pushClassicArticle);
  } else {
    // else pushing classic articles, then formatted typed, then typed
    articles.filter(
        (article) => (!articleTypes.includes(article["article_type"]))
    ).forEach(pushClassicArticle);
    articleTypes.forEach(pushTypedArticles);
    articles.filter(
        (article) => (articleTypes.includes(article["article_type"]))
    ).forEach(pushClassicArticle);
  }
  return (
    <>
      <Tabs indicatorColor="primary" textColor="primary"
        variant="scrollable" scrollButtons="auto"
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
  contents: PropTypes.array,
  feedTitle: PropTypes.string,
  autoplayChain: PropTypes.bool,
  clusters: PropTypes.array,
  currentClusterId: PropTypes.number,
  icons: PropTypes.object,
  filter: PropTypes.string,
  fetchCluster: PropTypes.func.isRequired,
  skipToNextMediaRequested: PropTypes.bool.isRequired,
  forceAutoplayNextMedia: PropTypes.bool.isRequired,
  clearSkipRequest: PropTypes.func.isRequired,
  clearForceAutoplayFlag: PropTypes.func.isRequired,
};
export default connect(mapStateToProps, mapDispatchToProps)(Articles);
